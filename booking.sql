CREATE TABLE "bookings" (
  "booking_id" varchar(36) NOT NULL,
  "guest_name" varchar(255) NOT NULL,
  "room_id" varchar(36),
  "check_in" date NOT NULL,
  "check_out" date NOT NULL,
  "status" varchar(20) DEFAULT 'активна'::character varying,
  "price_per_night" numeric(10,2) NOT NULL,
  PRIMARY KEY ("booking_id")
);
