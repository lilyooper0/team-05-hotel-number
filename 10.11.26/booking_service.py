import uuid
from src.models import Booking
from src.logger import log_action

class Result:
    def __init__(self, success, message):
        self.success = success
        self.message = message
def create_booking(storage, guest, room_id, check_in, check_out, price=1000.0):
    if not guest or not guest.strip():
        return Result(False, "Имя пустое.")
    if check_out <= check_in:
        return Result(False, "Выезд должен быть позже заезда.")

    b = Booking(str(uuid.uuid4())[:6], guest.strip(), room_id, check_in, check_out, "активна", price)
    storage.add(b)
    return Result(True, f"Бронь {b.id} создана.")

def cancel_booking(storage, booking_id):
    b = storage.find_by_id(booking_id)
    if b is None:
        log_action("cancel", booking_id, "error: unknown")
        return Result(False, "Не найдена.")
    if b.status == "отменена":
        log_action("cancel", booking_id, "error: already cancelled")
        return Result(False, "Уже отменена.")

    b.status = "отменена"
    storage.update(b)
    log_action("cancel", booking_id, "ok")
    return Result(True, "Отменена.")
