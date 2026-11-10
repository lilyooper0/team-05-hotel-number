# проверяет, что бронь и период допустимы, свободен ли номер
from datetime import date

from src.models import Booking, STATUS_ACTIVE


class ValidationError(ValueError):
    """Ошибка полей брони, периода или пересечения."""


#Поля и период

def validate_period(check_in: date, check_out: date) -> None:
    """Выезд строго позже заезда. Иначе ValidationError."""
    if check_in >= check_out:
        raise ValidationError(
            f"Дата выезда {check_out} должна быть строго позже "
            f"даты заезда {check_in}"
        )


def validate_booking_fields(
    guest_name: str,
    room_id: str,
    check_in: date,
    check_out: date,
    known_room_ids: set[str],
) -> None:
    """Проверка полей брони: имя, номер, период."""
    if not guest_name or not guest_name.strip():
        raise ValidationError("Имя гостя не может быть пустым")
    if room_id not in known_room_ids:
        raise ValidationError(f"Номер '{room_id}' не найден в справочнике")
    validate_period(check_in, check_out)


#Пересечения (единая функция)

def periods_overlap(
    a_in: date, a_out: date, b_in: date, b_out: date
) -> bool:
    """Пересечение периодов [in, out). Заезд включается, выезд нет.

    Смежные периоды (a_out == b_in) НЕ пересекаются.
    """
    return a_in < b_out and b_in < a_out


#Доступность 

def is_room_free(
    bookings: list[Booking],
    room_id: str,
    check_in: date,
    check_out: date,
) -> bool:
    """Свободен ли номер: нет пересечения с АКТИВНЫМИ бронями.

    Отменённые брони номер не занимают.
    """
    for b in bookings:
        if b.room_id == room_id and b.status == STATUS_ACTIVE:
            if periods_overlap(check_in, check_out, b.check_in, b.check_out):
                return False
    return True


def find_free_rooms(
    rooms: list,
    bookings: list[Booking],
    check_in: date,
    check_out: date,
) -> list[str]:
    """Номера без пересечения активных броней с периодом, по возрастанию id."""
    validate_period(check_in, check_out)
    return sorted(
        r.room_id for r in rooms
        if is_room_free(bookings, r.room_id, check_in, check_out)
    )
