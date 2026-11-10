"""Поиск доступных номеров за период.

Номер доступен, если ни одна АКТИВНАЯ бронь не пересекается
с запрошенным периодом. Отменённые брони номер не занимают.
"""
from datetime import date

from src.validation import _as_date, active_bookings_for_room, periods_overlap


def validate_period(check_in, check_out) -> tuple[date, date]:
    """Проверка запрошенного периода. Бросает ValueError с объяснением."""
    try:
        start = _as_date(check_in)
    except (ValueError, TypeError):
        raise ValueError(f"check_in: некорректная дата '{check_in}'")
    try:
        end = _as_date(check_out)
    except (ValueError, TypeError):
        raise ValueError(f"check_out: некорректная дата '{check_out}'")
    if end <= start:
        raise ValueError("Дата выезда должна быть строго позже даты заезда")
    return start, end


def is_room_available(
    bookings: list,
    room_id,
    check_in,
    check_out,
) -> bool:
    """Доступен ли номер за период [check_in, check_out)."""
    start, end = validate_period(check_in, check_out)
    for b in active_bookings_for_room(bookings, room_id):
        b_start = _as_date(b["check_in"])
        b_end = _as_date(b["check_out"])
        if periods_overlap(start, end, b_start, b_end):
            return False
    return True


def find_available_rooms(
    bookings: list,
    room_ids: list,
    check_in,
    check_out,
) -> list:
    """Список доступных номеров за период.

    room_ids — все существующие номера (из справочника rooms).
    Строки упорядочены по room_id (как в отчётах).
    Неверный период — ValueError с объяснением.
    """
    start, end = validate_period(check_in, check_out)
    available = []
    for rid in sorted(room_ids, key=str):
        if is_room_available(bookings, rid, start, end):
            available.append(rid)
    return available
