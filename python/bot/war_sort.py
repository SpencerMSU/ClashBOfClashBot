"""
Типы сортировки войн для бота Clash of Clans.
"""
from enum import Enum


class WarSort(Enum):
    """
    Перечисление типов сортировки истории войн.
    """
    DATE_DESC = "DATE_DESC"  # Сначала новые
    DATE_ASC = "DATE_ASC"    # Сначала старые
    CWL_ONLY = "CWL_ONLY"    # Только ЛВК за текущий месяц