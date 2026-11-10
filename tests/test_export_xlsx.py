import os
from datetime import date

from openpyxl import load_workbook

from src.models import Booking, STATUS_ACTIVE
from src.export_xlsx import export_xlsx


def make_booking(bid="B-001", guest="Гость", room_id="1",
                 check_in=date(2026, 11, 9), check_out=date(2026, 11, 12),
                 status=STATUS_ACTIVE, price=1000.0):
    return Booking(bid, guest, room_id, check_in, check_out, status, price)


def test_export_empty_creates_headers_and_zeros(tmp_path):
    path = os.path.join(str(tmp_path), "report.xlsx")
    r = export_xlsx(path, [], ["1", "2"])
    assert r["ok"] is True

    wb = load_workbook(path)
    assert wb.sheetnames == ["Данные", "Итоги"]

    ws_data = wb["Данные"]
    assert ws_data["A1"].value == "booking_id"
    assert ws_data.max_row == 1

    ws_sum = wb["Итоги"]
    rows = {r[0]: r[1] for r in ws_sum.iter_rows(values_only=True)
            if r[0] in ("active_count", "cancelled_count", "active_total")}
    assert rows["active_count"] == 0
    assert rows["cancelled_count"] == 0
    assert rows["active_total"] == 0


def test_export_acceptance_6(tmp_path):
    bookings = [
        make_booking(room_id="1", check_in=date(2026, 11, 9),
                     check_out=date(2026, 11, 12),
                     status=STATUS_ACTIVE, bid="B-001"),
        make_booking(room_id="1", check_in=date(2026, 11, 12),
                     check_out=date(2026, 11, 14),
                     status="отменена", bid="B-002"),
    ]
    path = os.path.join(str(tmp_path), "report.xlsx")
    r = export_xlsx(path, bookings, ["1", "2"])
    assert r["ok"] is True

    wb = load_workbook(path)

    ws_data = wb["Данные"]
    assert ws_data.max_row == 3  # заголовок + 2 брони

    ws_sum = wb["Итоги"]
    rows = list(ws_sum.iter_rows(values_only=True))

    totals = {row[0]: row[1] for row in rows
              if row[0] in ("active_count", "cancelled_count", "active_total")}
    assert totals["active_count"] == 1
    assert totals["cancelled_count"] == 1
    assert totals["active_total"] == 3000.0

    room_rows = {row[0]: row[1:] for row in rows
                 if row[0] in ("1", "2") and row[1] is not None}
    assert room_rows["1"] == (1, 3, 3000.0)
    assert room_rows["2"] == (0, 0, 0)


def test_export_refuses_overwrite_without_confirm(tmp_path):
    path = os.path.join(str(tmp_path), "report.xlsx")
    export_xlsx(path, [], ["1"])
    r = export_xlsx(path, [], ["1"], overwrite=False)
    assert r["ok"] is False
    assert "подтверждение" in r["reason"]


def test_export_overwrite_with_confirm(tmp_path):
    path = os.path.join(str(tmp_path), "report.xlsx")
    export_xlsx(path, [], ["1"])
    r = export_xlsx(path, [make_booking()], ["1"], overwrite=True)
    assert r["ok"] is True


def test_export_does_not_change_bookings(tmp_path):
    bookings = [make_booking()]
    snapshot = [
        (b.booking_id, b.guest_name, b.room_id,
         b.check_in, b.check_out, b.status, b.price_per_night)
        for b in bookings
    ]
    path = os.path.join(str(tmp_path), "report.xlsx")
    export_xlsx(path, bookings, ["1"])
    after = [
        (b.booking_id, b.guest_name, b.room_id,
         b.check_in, b.check_out, b.status, b.price_per_night)
        for b in bookings
    ]
    assert snapshot == after


def test_export_data_sheet_has_nights_and_cost(tmp_path):
    bookings = [make_booking(check_in=date(2026, 11, 9),
                             check_out=date(2026, 11, 12), price=1000.0)]
    path = os.path.join(str(tmp_path), "report.xlsx")
    export_xlsx(path, bookings, ["1"])

    wb = load_workbook(path)
    ws = wb["Данные"]
    headers = [c.value for c in ws[1]]
    row = [c.value for c in ws[2]]
    data = dict(zip(headers, row))
    assert data["nights"] == 3
    assert data["cost"] == 3000.0
