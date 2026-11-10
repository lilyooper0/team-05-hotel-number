import uuid
from src.models import Booking
from src.logger import log_action

#класс для операций получ или нет
class Result:
    def __init__(self, success, message):
        self.success = success
        self.message = message


def create_booking(storage, guest, room_id, check_in, check_out, price=1000.0):
    #имя не должно быть пустым
    if not guest or not guest.strip():
        return Result(False, "Имя пустое.")
    #выезд должен быть строго позже заезда
    if check_out <= check_in:
        return Result(False, "Выезд должен быть позже заезда.")

    b = Booking(str(uuid.uuid4())[:6], guest.strip(), room_id, check_in, check_out, "активна", price)
    storage.add(b)
    return Result(True, f"Бронь {b.id} создана.")


def cancel_booking(storage, booking_id):
    #ищем бронь по id
    b = storage.find_by_id(booking_id)
    if b is None:
        log_action("cancel", booking_id, "error: unknown")  # пишем в лог, что брони нет
        return Result(False, "Не найдена.")
    #нельзя отменить уже отменённую бронь
    if b.status == "отменена":
        log_action("cancel", booking_id, "error: already cancelled")
        return Result(False, "Уже отменена.")

    #всё в порядке- тогда меняем статус и сохраняем
    b.status = "отменена"
    storage.update(b)
    log_action("cancel", booking_id, "ok")  #пишем в лог что отмена прошла успешно
    return Result(True, "Отменена.")
