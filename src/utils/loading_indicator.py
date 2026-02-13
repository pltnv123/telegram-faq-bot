"""Индикатор загрузки для длительных операций AI генерации."""

from __future__ import annotations

import asyncio
from datetime import datetime

from aiogram.types import Message
from beartype import beartype


class LoadingIndicator:
    """Управляет индикацией процесса генерации ответа."""

    # Анимированные фазы с частой сменой эмодзи (каждые 3-5 секунд)
    PHASES = [
        (0, "Думаю над вопросом 🤔"),
        (3, "Анализирую 💭"),
        (6, "Обрабатываю 🧠"),
        (9, "Формирую ответ 💡"),
        (12, "Проверяю детали ✨"),
        (15, "Пишу ответ ✍️"),
        (20, "Дополняю информацией 📝"),
        (25, "Уточняю формулировки 🎯"),
        (30, "Почти готово ⏳"),
        (35, "Последние штрихи ⌛"),
        (40, "Финализирую ⚡"),
        (50, "Ещё чуть-чуть 🔄"),
        (60, "Завершаю работу ✅"),
    ]

    # Специальные сообщения
    TIMEOUT_MESSAGE = "Генерация заняла много времени... Переключаюсь на базу знаний 🔍"
    FALLBACK_MESSAGE = "Ищу в базе знаний 📚"

    def __init__(
        self,
        message: Message,
        loading_message: Message,
        start_time: datetime,
    ) -> None:
        """Инициализация индикатора.

        Args:
            message: Исходное сообщение пользователя
            loading_message: Сообщение индикатора загрузки
            start_time: Время начала операции
        """
        self.user_message = message
        self.loading_message = loading_message
        self.start_time = start_time
        self._stopped = False
        self._tasks: list[asyncio.Task] = []

    @classmethod
    @beartype
    async def start(cls, message: Message) -> LoadingIndicator:
        """Запустить индикатор загрузки.

        Args:
            message: Сообщение пользователя

        Returns:
            LoadingIndicator: Запущенный индикатор
        """
        # Отправить начальное сообщение
        loading_msg = await message.answer(cls.PHASES[0][1])
        
        start_time = datetime.now()
        indicator = cls(message, loading_msg, start_time)

        # Запустить фоновые задачи
        indicator._tasks.append(
            asyncio.create_task(indicator._typing_indicator_loop())
        )
        indicator._tasks.append(
            asyncio.create_task(indicator._progress_update_loop())
        )

        return indicator

    async def _typing_indicator_loop(self) -> None:
        """Периодически отправлять typing indicator (каждые 4 сек)."""
        try:
            while not self._stopped:
                await self.user_message.bot.send_chat_action(
                    self.user_message.chat.id,
                    "typing"
                )
                await asyncio.sleep(4)  # Обновляем каждые 4 сек
        except asyncio.CancelledError:
            pass  # Задача отменена, это нормально
        except Exception as e:
            print(f"Error in typing indicator: {e}")

    async def _progress_update_loop(self) -> None:
        """Обновлять текст сообщения в зависимости от времени."""
        try:
            current_phase = 0
            
            while not self._stopped:
                # Вычислить прошедшее время
                elapsed = (datetime.now() - self.start_time).total_seconds()
                
                # Определить текущую фазу
                new_phase = 0
                for i, (threshold, _) in enumerate(self.PHASES):
                    if elapsed >= threshold:
                        new_phase = i
                
                # Обновить текст если фаза изменилась
                if new_phase != current_phase:
                    current_phase = new_phase
                    try:
                        await self.loading_message.edit_text(
                            self.PHASES[current_phase][1]
                        )
                    except Exception as e:
                        # Игнорируем ошибки редактирования (например, текст не изменился)
                        pass
                
                await asyncio.sleep(0.8)  # Проверяем каждые 0.8 секунды (более живо)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in progress update: {e}")

    @beartype
    async def update_phase(self, phase: str) -> None:
        """Вручную обновить фазу (для особых случаев).

        Args:
            phase: Название фазы ('timeout', 'fallback' или текст)
        """
        if self._stopped:
            return
            
        try:
            if phase == "timeout":
                await self.loading_message.edit_text(self.TIMEOUT_MESSAGE)
            elif phase == "fallback":
                await self.loading_message.edit_text(self.FALLBACK_MESSAGE)
            else:
                await self.loading_message.edit_text(phase)
        except Exception as e:
            print(f"Error updating phase: {e}")

    async def stop(self) -> None:
        """Остановить индикатор и удалить сообщение."""
        if self._stopped:
            return
            
        self._stopped = True
        
        # Отменить все фоновые задачи
        for task in self._tasks:
            if not task.done():
                task.cancel()
        
        # Дождаться завершения задач
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        
        # Удалить сообщение индикатора
        try:
            await self.loading_message.delete()
        except Exception as e:
            # Игнорируем ошибки удаления (сообщение уже могло быть удалено)
            print(f"Could not delete loading message: {e}")
