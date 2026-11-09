# каркас консольного меню
def main():
    while True:
        print("\n=== Бронирование гостиницы ===")
        print("1) Оформить бронь  2) Отменить бронь  3) Свободные номера")
        print("4) Отчёт           5) Импорт CSV      6) Выгрузка XLSX")
        print("0) Выход")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "0":
                break
              
            print("Модуль ещё не подключён.")
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()

