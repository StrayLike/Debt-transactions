# test_finance.py
# Автоматизований тест для перевірки логіки балансу та статусів
import json
import os
import main  # імпортуємо головний модуль

TEST_FILE = "test_data.json"

def setup(records):
    """Записує тестові дані у тимчасовий файл і підміняє константу."""
    main.DATA_FILE = TEST_FILE
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f)

def teardown():
    """Видаляє тимчасовий файл після тесту."""
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

print("Запуск автоматизованих тестів...\n")

# Тест 1: баланс при нормальних даних (Активні борги)
setup([
    {"id": 1, "creditor": "Максим", "debtor": "Олег", "amount": 1000.0, "is_returned": False},
    {"id": 2, "creditor": "Іван", "debtor": "Максим", "amount": 300.0, "is_returned": False}
])

records = main.load_data()
owed_to = sum(r["amount"] for r in records if r["creditor"] == "Максим" and not r["is_returned"])
owes = sum(r["amount"] for r in records if r["debtor"] == "Максим" and not r["is_returned"])
balance = round(owed_to - owes, 2)

assert balance == 700.0, f"Очікувалось 700.0, отримано {balance}"
print(" ✔ Тест 1: баланс (1000 - 300 = 700) — ПРОЙДЕНО")

# Тест 2: баланс при порожньому файлі
setup([])
records = main.load_data()
owed_to = sum(r["amount"] for r in records if r.get("creditor") == "Максим" and not r["is_returned"])
owes = sum(r["amount"] for r in records if r.get("debtor") == "Максим" and not r["is_returned"])
balance = round(owed_to - owes, 2)

assert balance == 0.0, f"Очікувалось 0.0, отримано {balance}"
print(" ✔ Тест 2: баланс при порожніх даних (0.0) — ПРОЙДЕНО")

# Тест 3: ігнорування повернутих боргів при підрахунку
setup([
    {"id": 1, "creditor": "Максим", "debtor": "Олег", "amount": 500.0, "is_returned": True},
    {"id": 2, "creditor": "Максим", "debtor": "Олег", "amount": 200.0, "is_returned": False}
])

records = main.load_data()
owed_to = sum(r["amount"] for r in records if r["creditor"] == "Максим" and not r["is_returned"])

assert owed_to == 200.0, f"Очікувалось 200.0, отримано {owed_to}"
print(" ✔ Тест 3: ігнорування повернутих боргів (статус is_returned) — ПРОЙДЕНО")

teardown()
print("\nУсі тести пройдено успішно!")