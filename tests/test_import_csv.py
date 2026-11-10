import os
import tempfile

from src.import_csv import import_csv


ROOMS = {"1": 1000.00, "2": 1500.00}

HEADER = "booking_id,guest_name,room_id,check_in,check_out,status,price_per_night\n"


def _write(tmp_path, content: str) -> str:
    p = os.path.join(tmp_path, "bookings.csv")
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


def test_import_valid_adds_all(tmp_path):
    content = HEADER + (
        "B-001,Иванов Иван,1,2026-11-09,2026-11-12,активна,1000.00\n"
        "B-002,Петров Пётр,2,2026-11-10,2026-11-14,отменена,1500.00\n"
    )
    p = _write(str(tmp_path), content)
    r = import_csv(p, ROOMS, [])
    assert r["ok"] is True
    assert len(r["added"]) == 2
    assert r["errors"] == []


def test_import_missing_column_rejects_file(tmp_path):
    content = "booking_id,guest_name,room_id\nB-001,Иван,1\n"
    p = _write(str(tmp_path), content)
    r = import_csv(p, ROOMS, [])
    assert r["ok"] is False
    assert r["added"] == []
    assert any("обязательных столбцов" in e[1] for e in r["errors"])


def test_import_unknown_room_rejects_whole_file(tmp_path):
    content = HEADER + (
        "B-001,Иванов Иван,1,2026-11-09,2026-11-12,активна,1000.00\n"
        "B-002,Петров Пётр,99,2026-11-10,2026-11-14,активна,1500.00\n"
    )
    p = _write(str(tmp_path), content)
    r = import_csv(p, ROOMS, [])
    assert r["ok"] is False
    assert r["added"] == []  # ни одна бронь не добавлена
    assert any(e[0] == 3 and "неизвестный номер" in e[1] for e in r["errors"])


def test_import_conflict_with_existing_rejects_whole_file(tmp_path):
    existing = [{
        "booking_id": "B-000", "guest_name": "Старый", "room_id": "1",
        "check_in": "2026-11-09", "check_out": "2026-11-12",
        "status": "активна", "price_per_night": 1000.00,
    }]
    content = HEADER + (
        "B-001,Новый,1,2026-11-11,2026-11-13,активна,1000.00\n"
    )
    p = _write(str(tmp_path), content)
    r = import_csv(p, ROOMS, existing)
    assert r["ok"] is False
    assert r["added"] == []
    assert any("пересекается" in e[1] for e in r["errors"])


def test_import_conflict_between_rows_in_file(tmp_path):
    content = HEADER + (
        "B-001,Первый,1,2026-11-09,2026-11-12,активна,1000.00\n"
        "B-002,Второй,1,2026-11-11,2026-11-13,активна,1000.00\n"
    )
    p = _write(str(tmp_path), content)
    r = import_csv(p, ROOMS, [])
    assert r["ok"] is False
    assert r["added"] == []
    assert any(e[0] == 3 and "пересекается" in e[1] for e in r["errors"])


def test_import_duplicate_id_in_file(tmp_path):
    content = HEADER + (
        "B-001,Первый,1,2026-11-09,2026-11-12,активна,1000.00\n"
        "B-001,Второй,2,2026-11-10,2026-11-14,активна,1500.00\n"
    )
    p = _write(str(tmp_path), content)
    r = import_csv(p, ROOMS, [])
    assert r["ok"] is False
    assert any("уже существует" in e[1] for e in r["errors"])


def test_import_bad_dates_and_empty_name(tmp_path):
    content = HEADER + (
        "B-001,,1,2026-11-12,2026-11-09,активна,1000.00\n"
    )
    p = _write(str(tmp_path), content)
    r = import_csv(p, ROOMS, [])
    assert r["ok"] is False
    reasons = " ".join(e[1] for e in r["errors"])
    assert "guest_name" in reasons
    assert "check_out" in reasons


def test_import_reports_all_errors(tmp_path):
    existing = [{
        "booking_id": "B-000", "guest_name": "Старый", "room_id": "1",
        "check_in": "2026-11-09", "check_out": "2026-11-12",
        "status": "активна", "price_per_night": 1000.00,
    }]
    content = HEADER + (
        "B-001,Новый,2,2026-11-10,2026-11-12,активна,1500.00\n"
        "B-002,Конфликт,1,2026-11-11,2026-11-13,активна,1000.00\n"
        "B-003,Неизвестный,99,2026-11-10,2026-11-12,активна,1000.00\n"
    )
    p = _write(str(tmp_path), content)
    r = import_csv(p, ROOMS, existing)
    assert r["ok"] is False
    assert r["added"] == []
    assert len(r["errors"]) >= 2
    reasons = " ".join(e[1] for e in r["errors"])
    assert "пересекается" in reasons
    assert "неизвестный номер" in reasons

