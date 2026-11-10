import sys
import os
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Booking
from src.storage import BookingStorage
from src.booking_service import create_booking, cancel_booking


#вспомогательная функция создаёт хранилище во временной папке
#и добавляет в него одну тестовую бронь B1
def get_test_storage(tmp_path):
    file_path = tmp_path / "bookings.csv"
    storage = BookingStorage(str(file_path))
    b = Booking("B1", "Иван", "1", date(2026, 11, 9), date(2026, 11, 12), "активна", 1000.0)
    storage.add(b)
    return storage


#тесты

def test_invalid_dates(tmp_path):
    #выезд раньше заезда - такое бронирование должно быть отклонено
    storage = get_test_storage(tmp_path)
    res = create_booking(storage, "Гость", "1", date(2026, 11, 12), date(2026, 11, 9))
    assert not res.success

def test_same_dates(tmp_path):
    #заезд и выезд в один день - должно быть отклонено
    storage = get_test_storage(tmp_path)
    res = create_booking(storage, "Гость", "1", date(2026, 11, 9), date(2026, 11, 9))
    assert not res.success

def test_empty_guest(tmp_path):
    #если имя из пробелов - то нельзя такое создать
    storage = get_test_storage(tmp_path)
    res = create_booking(storage, "   ", "1", date(2026, 11, 9), date(2026, 11, 12))
    assert not res.success

def test_create_success(tmp_path):
    #обычная корректная бронь - должна создаваться успешно
    storage = get_test_storage(tmp_path)
    res = create_booking(storage, "Петр", "2", date(2026, 11, 9), date(2026, 11, 12))
    assert res.success

def test_cancel_success(tmp_path):
    #отменяем существующую бронь B1 - успех и статус меняется на "отменена"
    storage = get_test_storage(tmp_path)
    res = cancel_booking(storage, "B1")
    assert res.success
    assert storage.find_by_id("B1").status == "отменена"

def test_cancel_unknown(tmp_path):
    #пытаемся отменить бронь, которой нет - должна быть ошибка
    storage = get_test_storage(tmp_path)
    res = cancel_booking(storage, "NOPE")
    assert not res.success

def test_cancel_twice(tmp_path):
    #нельзя отменить одну и ту же бронь дважды
    storage = get_test_storage(tmp_path)
    cancel_booking(storage, "B1")   #первая отмена - ок
    res = cancel_booking(storage, "B1")  #вторая отмена - уже ошибка
    assert not res.success
