import os

from openpyxl import Workbook
from openpyxl.styles import Font

from src.data_processing import (
    nights_count,
    booking_cost,
    total_report,
    room_report,
)


DATA_HEADERS = [
    "booking_id", "guest_name", "room_id",
    "check_in", "check_out", "status",
    "price_per_night", "nights", "cost",
]


def _booking_to_dict(b) -> dict:
    """Booking → dict для data_processing."""
    return {
        "booking_id": b.booking_id,
        "guest_name": b.guest_name,
        "room_id": b.room_id,
        "check_in": b.check_in.isoformat(),
        "check_out": b.check_out.isoformat(),
        "status": b.status,
        "price_per_night": b.price_per_night,
    }


def _write_data_sheet(ws, bookings: list) -> None:
    """Лист «Данные»: все брони + nights + cost."""
    ws.append(DATA_HEADERS)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for b in bookings:
        d = _booking_to_dict(b)
        n = nights_count(d["check_in"], d["check_out"])
        ws.append([
            d["booking_id"],
            d["guest_name"],
            d["room_id"],
            d["check_in"],
            d["check_out"],
            d["status"],
            float(d["price_per_night"]),
            n,
            booking_cost(d),
        ])
    for col, width in zip("ABCDEFGHI", [14, 24, 10, 12, 12, 12, 16, 10, 12]):
        ws.column_dimensions[col].width = width


def _write_summary_sheet(ws, bookings: list, room_ids: list) -> None:
    """Лист «Итоги»: общие показатели + разбивка по номерам."""
    as_dicts = [_booking_to_dict(b) for b in bookings]
    total = total_report(as_dicts)

    ws.append(["Общие показатели"])
    ws["A1"].font = Font(bold=True, size=12)
    ws.append(["active_count", total["active_count"]])
    ws.append(["cancelled_count", total["cancelled_count"]])
    ws.append(["active_total", total["active_total"]])

    ws.append([])
    ws.append(["Разбивка по номерам"])
    ws.cell(row=ws.max_row, column=1).font = Font(bold=True, size=12)
    ws.append(["room_id", "active_count", "nights", "total"])
    for cell in ws[ws.max_row]:
        cell.font = Font(bold=True)

    for r in room_report(as_dicts, room_ids):
        ws.append([r["room_id"], r["active_count"], r["nights"], r["total"]])

    for col, width in zip("ABCD", [14, 14, 10, 14]):
        ws.column_dimensions[col].width = width


def export_xlsx(
    path: str,
    bookings: list,
    room_ids: list,
    overwrite: bool = False,
) -> dict:

    if os.path.exists(path) and not overwrite:
        return {"ok": False,
                "reason": "файл существует, требуется подтверждение перезаписи"}

    try:
        wb = Workbook()
        ws_data = wb.active
        ws_data.title = "Данные"
        _write_data_sheet(ws_data, bookings)

        ws_summary = wb.create_sheet("Итоги")
        _write_summary_sheet(ws_summary, bookings, room_ids)

        tmp_path = path + ".tmp"
        wb.save(tmp_path)
        os.replace(tmp_path, path)
        return {"ok": True, "reason": "выгрузка выполнена"}
    except OSError as e:
        return {"ok": False, "reason": f"ошибка сохранения: {e}"}
