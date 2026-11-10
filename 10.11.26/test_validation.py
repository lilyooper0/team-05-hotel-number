from datetime import date

import pytest

from src.models import Booking, STATUS_ACTIVE
from src.validation import (
    ValidationError,
    validate_period,
    validate_booking_fields,
    periods_overlap,
    is_room_free,
    find_free_rooms,
)


#Вспомогательные 

def make_booking(bid="B-001", guest="Гость", room_id="1",
                 check_in=date(2026, 11, 9), check_out=date(2026, 11, 12),
                 status=STATUS_ACTIVE, price=1000.0):
    """Booking под конструктор models.py (позиционно)."""
    return Booking(bid, guest, room_id, check_in, check_out, status, price)


def make_room(room_id="1"):
    """Заглушка номера: find_free_rooms использует только r.room_id."""
    class Room:
        def __init__(self, rid):
            self.room_id = rid
    return Room(room_id)


#validate_period

def test_validate_period_ok():
    validate_period(date(2026, 11, 9), date(2026, 11, 12))


def test_validate_period_same_day_rejected():
    with pytest.raises(ValidationError, match="строго позже"):
        validate_period(date(2026, 11, 9), date(2026, 11, 9))


def test_validate_period_reverse_rejected():
    with pytest.raises(ValidationError, match="строго позже"):
        validate_period(date(2026, 11, 12), date(2026, 11, 9))


def test_validation_error_is_value_error():
    assert issubclass(ValidationError, ValueError)


#validate_booking_fields

def test_fields_ok():
    validate_booking_fields("Иван", "1",
                            date(2026, 11, 9), date(2026, 11, 12),
                            {"1", "2"})


def test_fields_empty_name_rejected():
    with pytest.raises(ValidationError, match="Имя гостя"):
        validate_booking_fields("   ", "1",
                                date(2026, 11, 9), date(2026, 11, 12),
                                {"1", "2"})


def test_fields_unknown_room_rejected():
    with pytest.raises(ValidationError, match="не найден"):
        validate_booking_fields("Иван", "99",
                                date(2026, 11, 9), date(2026, 11, 12),
                                {"1", "2"})


def test_fields_bad_period_rejected():
    with pytest.raises(ValidationError, match="строго позже"):
        validate_booking_fields("Иван", "1",
                                date(2026, 11, 12), date(2026, 11, 9),
                                {"1", "2"})


#periods_overlap

def test_overlap_inside():
    assert periods_overlap(date(2026, 11, 10), date(2026, 11, 11),
                           date(2026, 11, 9), date(2026, 11, 12)) is True


def test_overlap_partial_left():
    assert periods_overlap(date(2026, 11, 9), date(2026, 11, 11),
                           date(2026, 11, 10), date(2026, 11, 12)) is True


def test_overlap_partial_right():
    assert periods_overlap(date(2026, 11, 10), date(2026, 11, 12),
                           date(2026, 11, 9), date(2026, 11, 11)) is True


def test_overlap_contains():
    assert periods_overlap(date(2026, 11, 8), date(2026, 11, 13),
                           date(2026, 11, 9), date(2026, 11, 12)) is True


def test_overlap_same_period():
    assert periods_overlap(date(2026, 11, 9), date(2026, 11, 12),
                           date(2026, 11, 9), date(2026, 11, 12)) is True


def test_adjacent_not_overlap():
    # 9–12 и 12–14 — смежные, не пересекаются
    assert periods_overlap(date(2026, 11, 9), date(2026, 11, 12),
                           date(2026, 11, 12), date(2026, 11, 14)) is False


def test_disjoint_not_overlap():
    assert periods_overlap(date(2026, 11, 9), date(2026, 11, 10),
                           date(2026, 11, 11), date(2026, 11, 12)) is False


#is_room_free

def test_room_free_when_no_bookings():
    assert is_room_free([], "1",
                        date(2026, 11, 9), date(2026, 11, 12)) is True


def test_room_busy_on_overlap():
    bookings = [make_booking()]
    assert is_room_free(bookings, "1",
                        date(2026, 11, 11), date(2026, 11, 13)) is False


def test_room_free_adjacent():
    # 12–14 после 9–12 — доступен
    bookings = [make_booking()]
    assert is_room_free(bookings, "1",
                        date(2026, 11, 12), date(2026, 11, 14)) is True


def test_room_free_after_cancel():
    # Отменённая не занимает номер
    bookings = [make_booking(status="отменена")]
    assert is_room_free(bookings, "1",
                        date(2026, 11, 9), date(2026, 11, 12)) is True


def test_room_free_other_room_busy():
    bookings = [make_booking(room_id="1")]
    assert is_room_free(bookings, "2",
                        date(2026, 11, 9), date(2026, 11, 12)) is True


#find_free_rooms

def test_find_free_rooms_acceptance():
    # Номер 1 занят 9–12; 2 и 3 свободны
    bookings = [make_booking(room_id="1")]
    rooms = [make_room("1"), make_room("2"), make_room("3")]
    result = find_free_rooms(rooms, bookings,
                             date(2026, 11, 9), date(2026, 11, 12))
    assert result == ["2", "3"]


def test_find_free_rooms_sorted():
    result = find_free_rooms(
        [make_room("3"), make_room("1"), make_room("2")],
        [],
        date(2026, 11, 9), date(2026, 11, 12),
    )
    assert result == ["1", "2", "3"]


def test_find_free_rooms_all_busy():
    bookings = [
        make_booking(bid="B-001", room_id="1"),
        make_booking(bid="B-002", room_id="2"),
    ]
    rooms = [make_room("1"), make_room("2")]
    result = find_free_rooms(rooms, bookings,
                             date(2026, 11, 9), date(2026, 11, 12))
    assert result == []


def test_find_free_rooms_bad_period():
    with pytest.raises(ValidationError, match="строго позже"):
        find_free_rooms([make_room("1")], [],
                        date(2026, 11, 12), date(2026, 11, 9))


def test_find_free_rooms_cancelled_not_busy():
    bookings = [make_booking(room_id="1", status="отменена")]
    rooms = [make_room("1"), make_room("2")]
    result = find_free_rooms(rooms, bookings,
                             date(2026, 11, 9), date(2026, 11, 12))
    assert result == ["1", "2"]
