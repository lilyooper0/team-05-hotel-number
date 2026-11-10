import csv
from datetime import date

from src.models import Booking, STATUS_ACTIVE
from src.validation import periods_overlap


REQUIRED_COLUMNS = [
    "booking_id", "guest_name", "room_id",
    "check_in", "check_out", "status", "price_per_night",
]
VALID_STATUSES = {STATUS_ACTIVE, "отменена"}


def _get(obj, name, default=None):
    """Достаёт поле и из Booking (атрибут), и из dict (ключ)."""
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _to_date(value) -> date | None:
    """Строка ISO или date → date. None при ошибке."""
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def _parse_date(value: str, field: str, line_no: int, errors: list):
    d = _to_date(value)
    if d is None:
        errors.append((line_no, f"{field}: некорректная дата '{value}' (нужно ГГГГ-ММ-ДД)"))
    return d


def _parse_price(value: str, line_no: int, errors: list):
    try:
        price = float(value)
    except (ValueError, TypeError):
        errors.append((line_no, f"price_per_night: не число '{value}'"))
        return None
    if price <= 0:
        errors.append((line_no, f"price_per_night: должно быть > 0, получено {value}"))
        return None
    text = str(value)
    if "." in text:
        decimals = text.split(".", 1)[1]
        if len(decimals) > 2:
            errors.append((line_no, f"price_per_night: больше 2 знаков после запятой '{value}'"))
            return None
    return round(price, 2)


def validate_rows(rows: list, rooms: dict, existing_bookings: list):
    """Проверка строк CSV.

    existing_bookings может содержать Booking или dict.
    Возвращает (valid: list[Booking], errors: list[(line_no, reason)]).
    Собирает все ошибки строки, а не первую.
    """
    errors = []
    valid = []
    seen_ids = {_get(b, "booking_id") for b in existing_bookings}

    # активные периоды по номерам: из сохранённых
    active_by_room = {}
    for b in existing_bookings:
        if _get(b, "status") == STATUS_ACTIVE:
            start = _to_date(_get(b, "check_in"))
            end = _to_date(_get(b, "check_out"))
            if start and end:
                active_by_room.setdefault(str(_get(b, "room_id")), []).append((start, end))

    known_room_ids = {str(k) for k in rooms.keys()}

    for idx, row in enumerate(rows, start=2):
        before = len(errors)

        # 1) обязательные поля
        for col in REQUIRED_COLUMNS:
            if col not in row or row[col] is None or str(row[col]).strip() == "":
                errors.append((idx, f"{col}: обязательное поле пустое"))

        # даже если пустые поля есть — не выходим, проверим остальное,
        # что можем (даты/цену) — тест ждёт «все ошибки строки»
        booking_id = str(row.get("booking_id", "")).strip()
        guest_name = str(row.get("guest_name", "")).strip()
        room_id = str(row.get("room_id", "")).strip()
        status = str(row.get("status", "")).strip()

        # 2) уникальность id
        if booking_id and booking_id in seen_ids:
            errors.append((idx, f"booking_id '{booking_id}': уже существует"))

        # 3) существование номера
        if room_id and room_id not in known_room_ids:
            errors.append((idx, f"room_id '{room_id}': неизвестный номер"))

        # 4) статус
        if status and status not in VALID_STATUSES:
            errors.append((idx, f"status '{status}': допустимо 'активна' или 'отменена'"))

        # 5) даты
        check_in = _parse_date(str(row.get("check_in", "")).strip(),
                               "check_in", idx, errors)
        check_out = _parse_date(str(row.get("check_out", "")).strip(),
                                "check_out", idx, errors)
        if check_in and check_out and check_out <= check_in:
            errors.append((idx, "check_out: должна быть строго позже check_in"))

        # 6) цена
        price = _parse_price(str(row.get("price_per_night", "")).strip(),
                             idx, errors)

        # 7) если по строке уже есть ошибки — не проверяем пересечения
        if len(errors) > before:
            continue

        # 8) пересечения активных (с сохранёнными и другими строками файла)
        if status == STATUS_ACTIVE:
            for (start, end) in active_by_room.get(room_id, []):
                if periods_overlap(check_in, check_out, start, end):
                    errors.append((
                        idx,
                        f"room_id '{room_id}': период {check_in}–{check_out} "
                        f"пересекается с активной бронью {start}–{end}",
                    ))
                    break

        if len(errors) > before:
            continue

        # 9) строка валидна — создаём Booking
        booking = Booking(
            booking_id, guest_name, room_id,
            check_in, check_out, status, price,
        )
        valid.append(booking)
        seen_ids.add(booking_id)
        if status == STATUS_ACTIVE:
            active_by_room.setdefault(room_id, []).append((check_in, check_out))

    return valid, errors


def import_csv(path: str, rooms: dict, existing_bookings: list) -> dict:
    """Импорт CSV. 

    Возвращает {"ok": bool, "added": list[Booking], "errors": [(line_no, reason)]}.
    При ошибке added = [], состояние не меняется.
    """
    rows = []

    try:
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return {"ok": False, "added": [],
                        "errors": [(1, "файл пуст или нет заголовков")]}
            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                return {"ok": False, "added": [],
                        "errors": [(1, f"нет обязательных столбцов: {', '.join(missing)}")]}
            for row in reader:
                rows.append(row)
    except FileNotFoundError:
        return {"ok": False, "added": [], "errors": [(0, f"файл не найден: {path}")]}
    except UnicodeDecodeError:
        return {"ok": False, "added": [], "errors": [(0, "файл не в кодировке UTF-8")]}
    except OSError as e:
        return {"ok": False, "added": [], "errors": [(0, f"ошибка чтения: {e}")]}

    valid, errors = validate_rows(rows, rooms, existing_bookings)

    if errors:
        return {"ok": False, "added": [], "errors": errors}
    return {"ok": True, "added": valid, "errors": []}
