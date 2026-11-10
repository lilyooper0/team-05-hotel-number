# Проверка пересечений и доступность (Lead Developer)

## Единая проверка пересечений — `src/validation.py`
- `periods_overlap(a_start, a_end, b_start, b_end)` — единственная
  функция пересечения. Период [start, end): заезд включается,
  выезд нет. Смежные периоды НЕ пересекаются.
- `find_conflict(bookings, room_id, check_in, check_out, exclude_booking_id=None)`
  — возвращает первую конфликтующую активную бронь или None.
- `ensure_no_conflict(...)` — бросает ValueError при конфликте.

**Используется:**
- оформление брони — `src/booking_service.py` (Рыбакова);
- импорт CSV — `src/import_csv.py` (Нурбекова);
- поиск доступности — `src/availability.py`.

Отменённые брони номер не занимают.

## Поиск доступности — `src/availability.py`
- `validate_period(check_in, check_out)` — проверка периода,
  ValueError с объяснением при неверных датах.
- `is_room_available(bookings, room_id, check_in, check_out)` — bool.
- `find_available_rooms(bookings, room_ids, check_in, check_out)` —
  список доступных номеров, сортировка по room_id.

## Соглашение
Одна проверка пересечений для оформления и импорта — прямое
требование ТЗ. Дублировать логику в других модулях нельзя.
