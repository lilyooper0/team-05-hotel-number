# models.py — общий модуль, правит Lead Developer (ты), изменения только через согласование
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

STATUS_ACTIVE = "активна"
STATUS_CANCELLED = "отменена"

@dataclass(frozen=True)
class Room:
    room_id: str            # уникальный идентификатор, например "101"
    price_per_night: Decimal  # > 0, два знака после запятой

@dataclass(frozen=True)
class Booking:
    booking_id: str         # уникальный идентификатор
    guest_name: str         # непустая строка
    room_id: str            # должен существовать в справочнике номеров
    check_in: date          # ГГГГ-ММ-ДД, день заезда ВКЛЮЧЁН
    check_out: date         # ГГГГ-ММ-ДД, день выезда НЕ включён
    status: str             # STATUS_ACTIVE или STATUS_CANCELLED
    price_per_night: Decimal  # цена на момент оформления

