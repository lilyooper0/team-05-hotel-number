"""Модуль обработки данных: расчёт ночей, стоимости и отчёты.

Форматы CSV/XLSX согласованы в docs/formats.md.
Схема данных описана в docs/data_model.md.

Функции не зависят от кода оформления брони: принимают список броней
(список словарей) и работают с ним. Источник данных (оформление,
импорт CSV, тест) для модуля не важен.
"""
from datetime import date


STATUS_ACTIVE = "активна"
STATUS_CANCELLED = "отменена"


def nights_count(check_in: str, check_out: str) -> int:
    """Число ночей: день заезда включается, день выезда — нет.

    Даты — строки ISO ГГГГ-ММ-ДД. Если check_out <= check_in — ValueError.
    """
    d1 = date.fromisoformat(check_in)
    d2 = date.fromisoformat(check_out)
    if d2 <= d1:
        raise ValueError("Дата выезда должна быть строго позже даты заезда")
    return (d2 - d1).days


def booking_cost(booking: dict) -> float:
    """Стоимость брони = ночи * сохранённая цена за ночь, округление до 2 знаков."""
    n = nights_count(booking["check_in"], booking["check_out"])
    return round(n * float(booking["price_per_night"]), 2)


def total_report(bookings: list) -> dict:
    """Общий отчёт: число активных, число отменённых, сумма стоимости активных."""
    active = [b for b in bookings if b["status"] == STATUS_ACTIVE]
    cancelled = [b for b in bookings if b["status"] == STATUS_CANCELLED]
    return {
        "active_count": len(active),
        "cancelled_count": len(cancelled),
        "active_total": round(sum(booking_cost(b) for b in active), 2),
    }


def room_report(bookings: list, room_ids: list) -> list:
    """Отчёт по номерам.

    Для каждого существующего номера: число активных броней, число ночей
    по ним и суммарная стоимость. Отменённые не участвуют.
    Строки упорядочены по идентификатору номера.
    Сумма стоимости строк совпадает с total_report()["active_total"].
    """
    result = []
    for rid in sorted(room_ids, key=str):
        active = [
            b for b in bookings
            if str(b["room_id"]) == str(rid) and b["status"] == STATUS_ACTIVE
        ]
        nights = sum(nights_count(b["check_in"], b["check_out"]) for b in active)
        total = round(sum(booking_cost(b) for b in active), 2)
        result.append({
            "room_id": rid,
            "active_count": len(active),
            "nights": nights,
            "total": total,
        })
    return result
