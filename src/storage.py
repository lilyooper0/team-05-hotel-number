import csv
import os
from src.models import Booking

FIELDS = ["id", "guest", "room_id", "check_in", "check_out", "status", "price"]

class BookingStorage:
    def __init__(self, path="data/bookings.csv"):
        self.path = path
        self.bookings = []
        self.load()  # сразу грузим данные из файла

    def load(self):
        # если файла нет — просто создаём папку и выходим
        if not os.path.exists(self.path):
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            return

        try:
            with open(self.path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    b = Booking("", "", "", None, None, "", 0)
                    b.from_row(row)  # заполняем объект из строки CSV
                    self.bookings.append(b)
        except Exception as e:
            raise RuntimeError(f"Ошибка чтения: {e}")

    def save(self):
        tmp = self.path + ".tmp"  # пишем во временный файл, чтобы не потерять данные при сбое
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)

            with open(tmp, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=FIELDS)
                w.writeheader()
                for b in self.bookings:
                    w.writerow(b.to_row())  # превращаем объект в строку CSV

            os.replace(tmp, self.path)  # безопасно заменяем старый файл новым
        except Exception as e:
            if os.path.exists(tmp):
                os.remove(tmp)
            raise RuntimeError(f"Ошибка сохранения: {e}")

    def add(self, booking):
        self.bookings.append(booking)
        self.save()  # сразу сохраняем

    def find_by_id(self, booking_id):
        for b in self.bookings:
            if b.id == booking_id:
                return b
        return None

    def update(self, booking):
        for i, b in enumerate(self.bookings):
            if b.id == booking.id:
                self.bookings[i] = booking  # обновляем в списке
                break
        self.save()  # и сразу пишем на диск

