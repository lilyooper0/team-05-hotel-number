import logging
import os

def log_action(operation, target, result):
    # Создаем папку logs, если её нет
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename="logs/app.log",
        level=logging.INFO,
        format="%(asctime)s | %(message)s",
        encoding="utf-8",
    )
    logging.info("%s | %s | %s", operation, target, result)
