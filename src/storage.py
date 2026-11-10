import csv
import os
from src.models import Booking

#названия колонок в CSV-файле
FIELDS = ["id", "guest", "room_id", "check_in", "check_out", "status", "price"]


class BookingStorage:
    def __init__(self, path="data/bookings.csv"):
        self.path = path
        self.bookings = []
        self.load()

    def load(self):
        if not os.path.exists(self.path):
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            return
        try:
            #из словаря делаем объект booking
            with open(self.path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    b = Booking("", "", "", None, None, "", 0)  #пустой объект
                    b.from_row(row)                             #заполняем его данными из строки
                    self.bookings.append(b)
        except Exception as e:
            #если файл поврежден - ошибка
            raise RuntimeError(f"Ошибка чтения: {e}")

    def save(self):
        #сохраняем всё в файл. Пишем сначала во временный файл (.tmp),
        #а потом заменяем им основной чтобы данные не потерялись при сбое
        tmp = self.path + ".tmp"
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(tmp, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=FIELDS)
                w.writeheader()                 #пишем строку с названиями колонок
                for b in self.bookings:
                    w.writerow(b.to_row())      #каждую бронь превращаем в строку
            os.replace(tmp, self.path)          #временный файл становится основным
        except Exception as e:
            #при ошибке удаляем временный файл
            if os.path.exists(tmp):
                os.remove(tmp)
            raise RuntimeError(f"Ошибка сохранения: {e}")

    def add(self, booking):
        #добавляем новую бронь в список и сразу сохраняем в файл
        self.bookings.append(booking)
        self.save()

    def find_by_id(self, booking_id):
        #ищем бронь по id и если не нашли то возвращаем None
        for b in self.bookings:
            if b.id == booking_id:
                return b
        return None

    def update(self, booking):
        #находим бронь с таким же id и заменяем её новой версией
        for i, b in enumerate(self.bookings):
            if b.id == booking.id:
                self.bookings[i] = booking
                break
        self.save()
