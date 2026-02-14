"""HTTP клиент для работы с Ollama API."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

import aiohttp
from beartype import beartype

# Настройка логгера для модуля
logger = logging.getLogger(__name__)


@beartype
class OllamaClient:
    """Клиент для взаимодействия с Ollama API."""

    def __init__(
        self,
        api_url: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> None:
        """Инициализация клиента.

        Args:
            api_url: URL Ollama API (например, http://localhost:11434)
            model: Название модели (например, llama3.2:3b)
            temperature: Температура генерации (0.0 - 1.0)
            max_tokens: Максимальная длина ответа в токенах
        """
        self.api_url = api_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Получить или создать aiohttp сессию.

        Returns:
            aiohttp.ClientSession: HTTP сессия
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Закрыть HTTP сессию."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def check_health(self) -> bool:
        """Проверить доступность Ollama API.

        Returns:
            bool: True если Ollama доступна
        """
        try:
            session = await self._get_session()
            async with session.get(
                f"{self.api_url}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                return response.status == 200
        except Exception:
            return False

    async def generate_response(
        self,
        prompt: str,
        max_retries: int = 3,
    ) -> str | None:
        """Сгенерировать ответ с помощью Ollama.

        Args:
            prompt: Полный промпт для генерации
            max_retries: Максимальное количество попыток

        Returns:
            str | None: Сгенерированный ответ или None при ошибке
        """
        session = await self._get_session()

        for attempt in range(max_retries):
            try:
                async with session.post(
                    f"{self.api_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": self.temperature,
                            "num_predict": self.max_tokens,
                        },
                    },
                    timeout=aiohttp.ClientTimeout(total=90),  # Увеличен до 90 сек для первого запроса
                ) as response:
                    if response.status == 200:
                        data: dict[str, Any] = await response.json()
                        return data.get("response", "").strip()
                    elif 500 <= response.status < 600:
                        # 5xx ошибки - серверные, временные, делаем retry
                        error_text = await response.text()
                        logger.warning(f"Ollama server error {response.status} (attempt {attempt + 1}/{max_retries}): {error_text}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        # 4xx ошибки - клиентские, не ретраим
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {response.status} - {error_text}")
                        return None

            except asyncio.TimeoutError:
                logger.warning(f"Ollama timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка
            except Exception as e:
                logger.error(f"Ollama error: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        return None

    async def chat(
        self,
        messages: list[dict[str, str]],
        max_retries: int = 3,
    ) -> str | None:
        """Отправить чат-сообщения в Ollama (chat API).

        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}]
            max_retries: Максимальное количество попыток

        Returns:
            str | None: Ответ ассистента или None при ошибке
        """
        session = await self._get_session()

        for attempt in range(max_retries):
            try:
                async with session.post(
                    f"{self.api_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": self.temperature,
                            "num_predict": self.max_tokens,
                        },
                    },
                    timeout=aiohttp.ClientTimeout(total=90),  # Увеличен до 90 сек для первого запроса
                ) as response:
                    if response.status == 200:
                        data: dict[str, Any] = await response.json()
                        message = data.get("message", {})
                        return message.get("content", "").strip()
                    elif 500 <= response.status < 600:
                        # 5xx ошибки - серверные, временные, делаем retry
                        error_text = await response.text()
                        logger.warning(f"Ollama server error {response.status} (attempt {attempt + 1}/{max_retries}): {error_text}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        # 4xx ошибки - клиентские, не ретраим
                        error_text = await response.text()
                        logger.error(f"Ollama chat API error: {response.status} - {error_text}")
                        return None

            except asyncio.TimeoutError:
                logger.warning(f"Ollama timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Ollama error: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        return None

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        on_token: Callable[[str], Awaitable[None]],
        max_retries: int = 3,
    ) -> str:
        """Отправить чат-сообщения с потоковой генерацией (streaming).

        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}]
            on_token: Callback функция для обработки каждого токена
            max_retries: Максимальное количество попыток

        Returns:
            str: Полный сгенерированный ответ

        Raises:
            Exception: При ошибке генерации после всех попыток
        """
        session = await self._get_session()

        for attempt in range(max_retries):
            try:
                async with session.post(
                    f"{self.api_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": True,  # Включаем streaming режим
                        "options": {
                            "temperature": self.temperature,
                            "num_predict": self.max_tokens,
                        },
                    },
                    timeout=aiohttp.ClientTimeout(total=120),  # Увеличен timeout для streaming
                ) as response:
                    if response.status == 200:
                        full_response = ""
                        
                        # Читаем поток построчно
                        async for line in response.content:
                            if not line:
                                continue
                            
                            try:
                                # Декодируем и парсим JSON
                                line_text = line.decode("utf-8").strip()
                                if not line_text:
                                    continue
                                
                                data = json.loads(line_text)
                                
                                # Извлекаем токен из сообщения
                                message = data.get("message", {})
                                token = message.get("content", "")
                                
                                if token:
                                    full_response += token
                                    # Вызываем callback для обновления UI
                                    await on_token(token)
                                
                                # Проверяем конец генерации
                                if data.get("done", False):
                                    break
                                    
                            except json.JSONDecodeError as e:
                                logger.error(f"JSON decode error in streaming: {e}")
                                continue
                            except Exception as e:
                                logger.error(f"Error processing streaming chunk: {e}")
                                continue
                        
                        return full_response.strip()
                    elif 500 <= response.status < 600:
                        # 5xx ошибки - серверные, временные, делаем retry
                        error_text = await response.text()
                        logger.warning(f"Ollama streaming server error {response.status} (attempt {attempt + 1}/{max_retries}): {error_text}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        # 4xx ошибки - клиентские, не ретраим
                        error_text = await response.text()
                        logger.error(f"Ollama streaming error: {response.status} - {error_text}")
                        raise Exception(f"Ollama API error: {response.status}")

            except asyncio.TimeoutError:
                logger.warning(f"Ollama streaming timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Ollama streaming error: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        # Если все попытки не удались - выбрасываем исключение
        raise Exception("Failed to generate streaming response after all retries")
