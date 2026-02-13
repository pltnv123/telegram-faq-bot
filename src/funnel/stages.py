"""Определение этапов воронки и базовые структуры.

7 этапов воронки по стандарту:
1. Привлечение (Acquisition)
2. Квалификация (Qualification)
3. Оффер (Offer)
4. Закрытие (Closing)
5. Сопровождение (Support)
6. Возвраты/Претензии (Complaints)
7. Повторные продажи (Retention)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from beartype import beartype

if TYPE_CHECKING:
    from src.nlu.slot_extractor import SlotCollection


class FunnelStage(str, Enum):
    """Этапы воронки."""

    ACQUISITION = "acquisition"  # Привлечение
    QUALIFICATION = "qualification"  # Квалификация
    OFFER = "offer"  # Оффер
    CLOSING = "closing"  # Закрытие
    SUPPORT = "support"  # Сопровождение
    COMPLAINTS = "complaints"  # Возвраты/претензии
    RETENTION = "retention"  # Повторные продажи


@dataclass
class StageResult:
    """Результат обработки этапа воронки."""

    stage: FunnelStage
    success: bool
    response_text: str
    next_stage: FunnelStage | None = None
    requires_handoff: bool = False
    handoff_reason: str | None = None
    collected_slots: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)


class BaseFunnelStage:
    """Базовый класс для всех этапов воронки."""

    stage_name: FunnelStage

    @beartype
    def get_required_slots(self) -> list[str]:
        """Получить список обязательных слотов для этапа.

        Returns:
            list[str]: Список имён слотов
        """
        return []

    @beartype
    def get_exit_criteria(self) -> dict[str, str]:
        """Получить критерии выхода из этапа.

        Returns:
            dict: Описание критериев
        """
        return {}

    @beartype
    def suggest_next_action(self, slots: SlotCollection) -> str:
        """Предложить следующее действие (CTA) для пользователя.

        Args:
            slots: Собранные слоты

        Returns:
            str: Текст CTA
        """
        return ""

    @beartype
    def is_complete(self, slots: SlotCollection) -> bool:
        """Проверить завершён ли этап (все слоты собраны).

        Args:
            slots: Собранные слоты

        Returns:
            bool: True если этап завершён
        """
        required = self.get_required_slots()
        for slot_name in required:
            if slots.get_value(slot_name) is None:
                return False
        return True

    @beartype
    def get_next_stage(self, slots: SlotCollection) -> FunnelStage | None:
        """Определить следующий этап воронки.

        Args:
            slots: Собранные слоты

        Returns:
            FunnelStage | None: Следующий этап или None
        """
        return None


@dataclass
class FunnelContext:
    """Контекст текущего состояния воронки для пользователя."""

    user_id: int
    current_stage: FunnelStage
    slots: SlotCollection
    stage_entry_count: dict[FunnelStage, int] = field(default_factory=dict)
    last_stage_change: str | None = None  # timestamp

    @beartype
    def move_to_stage(self, new_stage: FunnelStage) -> None:
        """Переместить пользователя на новый этап.

        Args:
            new_stage: Новый этап
        """
        from datetime import datetime

        self.current_stage = new_stage
        self.last_stage_change = datetime.now().isoformat()

        # Счётчик входов в этап
        if new_stage not in self.stage_entry_count:
            self.stage_entry_count[new_stage] = 0
        self.stage_entry_count[new_stage] += 1

    @beartype
    def get_stage_visits(self, stage: FunnelStage) -> int:
        """Получить количество посещений этапа.

        Args:
            stage: Этап

        Returns:
            int: Количество посещений
        """
        return self.stage_entry_count.get(stage, 0)
