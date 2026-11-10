import uuid
from src.models import Booking
from src.logger import log_action

# Контейнер результата операции: успех/неудача + сообщение
class Result:
    def __init__(self, success, message):
        self.success = success
        self.message = message

def create_booking(storage, guest, room_id, check_in, check_out, price=1000.0):
    # Валидация имени гостя
    if not guest or not guest.strip():
        return Result(False, "Имя пустое.")

    # Даты: выезд должен быть строго позже заезда
    if check_out <= check_in:
        return Result(False, "Выезд должен быть позже заезда.")

    # Генерируем короткий уникальный ID и создаём объект бронирования
    b = Booking(
        str(uuid.uuid4())[:6],
        guest.strip(),
        room_id,
        check_in,
        check_out,
        "активна",
        price
    )

    # Сохраняем в хранилище (CSV)
    storage.add(b)
    return Result(True, f"Бронь {b.id} создана.")

def cancel_booking(storage, booking_id):
    # Ищем бронь по ID
    b = storage.find_by_id(booking_id)
    if b is None:
        log_action("cancel", booking_id, "error: unknown")
        return Result(False, "Не найдена.")

    # Если уже отменена — не делаем повторно
    if b.status == "отменена":
        log_action("cancel", booking_id, "error: already cancelled")
        return Result(False, "Уже отменена.")

    # Меняем статус и сохраняем
    b.status = "отменена"
    storage.update(b)

    log_action("cancel", booking_id, "ok")
    return Result(True, "Отменена.")
