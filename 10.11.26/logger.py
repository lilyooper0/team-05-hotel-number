import logging
import os

def log_action(operation, target, result):
    #создаём папку logs
    os.makedirs("logs", exist_ok=True)
    
    #настраиваем логирование в файл app.log
    logging.basicConfig(
        filename="logs/app.log",
        level=logging.INFO,
        format="%(asctime)s | %(message)s",
        encoding="utf-8",
    )
    
    #операция, цель, результат
    logging.info("%s | %s | %s", operation, target, result)
