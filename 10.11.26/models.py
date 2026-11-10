from datetime import date

class Booking:
    def __init__(self, id, guest, room_id, check_in, check_out, status, price):
        self.id = id
        self.guest = guest
        self.room_id = room_id
        self.check_in = check_in
        self.check_out = check_out
        self.status = status
        self.price = price

    def to_row(self):
        return {
            "id": self.id, "guest": self.guest, "room_id": self.room_id,
            "check_in": self.check_in.isoformat(), "check_out": self.check_out.isoformat(),
            "status": self.status, "price": f"{self.price:.2f}",
        }

    def from_row(self, r):
        self.id = r["id"]
        self.guest = r["guest"]
        self.room_id = r["room_id"]
        self.check_in = date.fromisoformat(r["check_in"])
        self.check_out = date.fromisoformat(r["check_out"])
        self.status = r["status"]
        self.price = float(r["price"])
        return self
