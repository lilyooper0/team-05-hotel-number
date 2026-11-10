"""Модульные тесты расчётов и отчётов"""
import pytest

from src.data_processing import (
    nights_count,
    booking_cost,
    total_report,
    room_report,
)


def _booking(room_id="1", check_in="2026-11-09", check_out="2026-11-12",
             price="1000.00", status="активна", bid="B-001", guest="Гость"):
    return {
        "booking_id": bid,
        "guest_name": guest,
        "room_id": room_id,
        "check_in": check_in,
        "check_out": check_out,
        "status": status,
        "price_per_night": price,
    }


# --- ночи ---

def test_nights_count_acceptance():
    # Приёмка: 9–12 ноября = 3 ночи
    assert nights_count("2026-11-09", "2026-11-12") == 3


def test_nights_count_same_day_rejected():
    with pytest.raises(ValueError):
        nights_count("2026-11-12", "2026-11-12")


def test_nights_count_reverse_rejected():
    with pytest.raises(ValueError):
        nights_count("2026-11-12", "2026-11-09")


# --- стоимость ---

def test_booking_cost_acceptance():
    # Приёмка: цена 1000, 9–12 ноября → 3000.00
    assert booking_cost(_booking()) == 3000.00


def test_booking_cost_rounds_two_decimals():
    b = _booking(price="1234.56", check_in="2026-11-09", check_out="2026-11-11")
    assert booking_cost(b) == 2469.12


# --- общий отчёт ---

def test_total_report_empty():
    assert total_report([]) == {
        "active_count": 0, "cancelled_count": 0, "active_total": 0.0,
    }


def test_total_report_excludes_cancelled():
    bookings = [
        _booking(bid="B-001", status="активна"),
        _booking(bid="B-002", check_in="2026-11-12", check_out="2026-11-14",
                 status="отменена"),
    ]
    r = total_report(bookings)
    assert r["active_count"] == 1
    assert r["cancelled_count"] == 1
    assert r["active_total"] == 3000.00


# --- отчёт по номерам ---

def test_room_report_acceptance_6():
    # Приёмка №6: номер 1 — активная 9–12 и отменённая 12–14; номер 2 свободен.
    bookings = [
        _booking(room_id="1", check_in="2026-11-09", check_out="2026-11-12",
                 status="активна"),
        _booking(room_id="1", check_in="2026-11-12", check_out="2026-11-14",
                 status="отменена"),
    ]
    rows = room_report(bookings, ["1", "2"])
    assert rows[0] == {"room_id": "1", "active_count": 1,
                       "nights": 3, "total": 3000.00}
    assert rows[1] == {"room_id": "2", "active_count": 0,
                       "nights": 0, "total": 0}
    # Сумма строк = общий итог
    assert sum(r["total"] for r in rows) == total_report(bookings)["active_total"] == 3000.00


def test_room_report_includes_all_rooms_sorted():
    bookings = [_booking(room_id="2", bid="B-002")]
    rows = room_report(bookings, ["3", "1", "2"])
    assert [r["room_id"] for r in rows] == ["1", "2", "3"]


def test_room_report_no_bookings():
    rows = room_report([], ["1", "2"])
    assert all(r["active_count"] == 0 and r["nights"] == 0 and r["total"] == 0
               for r in rows)
