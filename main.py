import json
import os
from datetime import datetime

DATA_FILE = "data.json"

# --- Робота з файлами ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(records):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

# --- Ядро логіки ---
def logic_add_record(records, creditor, debtor, amount, note, timestamp):
    new_id = 1 if not records else max(r.get("id", 0) for r in records) + 1
    records.append({
        "id": new_id,
        "creditor": creditor,
        "debtor": debtor,
        "amount": round(amount, 2),
        "timestamp": timestamp,
        "is_returned": False,
        "note": note
    })
    return 0

def logic_update_record(records, rec_id, updates):
    for r in records:
        if r.get("id") == rec_id:
            r.update(updates)
            return 0
    return 1

def logic_delete_record(records, rec_id):
    initial_len = len(records)
    records[:] = [r for r in records if r.get("id") != rec_id]
    if len(records) == initial_len:
        return 1
    return 0

def logic_import_json(records, filepath):
    if not os.path.exists(filepath):
        return 1
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            imported_data = json.load(f)
            for item in imported_data:
                if "creditor" in item and "debtor" in item and "amount" in item:
                    logic_add_record(
                        records, 
                        item["creditor"], 
                        item["debtor"], 
                        float(item["amount"]), 
                        item.get("note", ""), 
                        item.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    )
        return 0
    except Exception:
        return 2

# --- Інтерфейс користувача (CLI) ---
def print_records(records):
    if not records:
        print(" Записів немає.")
        return
    
    print(f" {'ID':<4} {'Кредитор':<15} {'Боржник':<15} {'Сума':>10} {'Статус':<12} {'Час':<20} {'Примітка'}")
    print(" " + "-" * 100)
    for r in records:
        # Використовуємо .get() для безпеки, якщо трапляться старі або зламані записи
        r_id = r.get("id", "?")
        creditor = r.get("creditor", "Невідомо")
        debtor = r.get("debtor", "Невідомо")
        amount = r.get("amount", 0.0)
        status = "Повернуто" if r.get("is_returned", False) else "Активний"
        timestamp = r.get("timestamp", "-")
        note = r.get("note", "")
        
        print(f" {r_id:<4} {creditor:<15} {debtor:<15} {amount:>10.2f} {status:<12} {timestamp:<20} {note}")

def ui_add_loan():
    print("\n--- Додавання нової позики (введіть 0 для відміни) ---")
    creditor = input(" Хто дав гроші (Кредитор)? : ").strip()
    if creditor == "0": return
    
    debtor = input(" Хто взяв гроші (Боржник)? : ").strip()
    if debtor == "0": return
    
    if not creditor or not debtor:
        print(" Помилка: імена не можуть бути порожніми.")
        return

    try:
        amount_str = input(" Сума: ").strip()
        if amount_str == "0": return
        amount = float(amount_str)
        if amount <= 0:
            print(" Помилка: сума має бути більшою за нуль.")
            return
    except ValueError:
        print(" Помилка: введіть коректне число.")
        return

    note = input(" Примітка (необов'язково, 0 для відміни): ").strip()
    if note == "0": return

    time_str = input(" Дата і час (напр. 2026-06-22 14:30) або Enter для поточного: ").strip()
    if time_str == "0": return
    
    if not time_str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        timestamp = time_str

    records = load_data()
    if logic_add_record(records, creditor, debtor, amount, note, timestamp) == 0:
        save_data(records)
        print(" Успіх: Запис додано!")

def ui_show_all():
    print("\n--- Перегляд позик ---")
    print(" 1. Показати всю таблицю")
    print(" 2. Знайти записи конкретної особи")
    choice = input(" Ваш вибір (або 0 для відміни): ").strip()
    
    if choice == "0": return
    
    records = load_data()
    
    if choice == "1":
        print_records(records)
    elif choice == "2":
        person = input(" Введіть ім'я особи для пошуку: ").strip().lower()
        if person == "0": return
        
        # Шукаємо особу і серед кредиторів, і серед боржників (ігноруючи регістр)
        filtered = [r for r in records if r.get("creditor", "").lower() == person or r.get("debtor", "").lower() == person]
        
        if not filtered:
            print(f"\n Записів для особи '{person}' не знайдено.")
        else:
            print(f"\n--- Записи для: {person.capitalize()} ---")
            print_records(filtered)
    else:
        print(" Невідомий вибір.")

def ui_edit_loan():
    print("\n--- Редагування запису (введіть 0 для відміни) ---")
    records = load_data()
    if not records:
        print(" Список порожній.")
        return
        
    try:
        id_str = input(" Введіть ID запису для редагування: ").strip()
        if id_str == "0": return
        rec_id = int(id_str)
    except ValueError:
        print(" Помилка: ID має бути числом.")
        return

    current_record = next((r for r in records if r.get("id") == rec_id), None)
    if not current_record:
        print(" Помилка: Запис не знайдено.")
        return

    print("\n Вводьте нові значення або натисніть Enter, щоб залишити поточне.")
    new_creditor = input(f" Кредитор [{current_record.get('creditor', '')}]: ").strip()
    new_debtor = input(f" Боржник [{current_record.get('debtor', '')}]: ").strip()
    
    new_amount_str = input(f" Сума [{current_record.get('amount', 0)}]: ").strip()
    new_amount = current_record.get('amount', 0)
    if new_amount_str:
        try:
            new_amount = float(new_amount_str)
        except ValueError:
            print(" Помилка: некоректна сума. Зміни скасовано.")
            return

    new_note = input(f" Примітка [{current_record.get('note', '')}]: ").strip()
    new_time = input(f" Час [{current_record.get('timestamp', '')}]: ").strip()

    updates = {}
    if new_creditor: updates["creditor"] = new_creditor
    if new_debtor: updates["debtor"] = new_debtor
    if new_amount_str: updates["amount"] = new_amount
    if new_note: updates["note"] = new_note
    if new_time: 
        updates["timestamp"] = new_time
    else:
        updates["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if logic_update_record(records, rec_id, updates) == 0:
        save_data(records)
        print(" Успіх: Запис оновлено!")

def ui_mark_returned():
    print("\n--- Позначити позику як повернуту (0 для відміни) ---")
    records = load_data()
    
    try:
        id_str = input(" Введіть ID позики, яку повернули: ").strip()
        if id_str == "0": return
        rec_id = int(id_str)
    except ValueError:
        print(" Помилка: ID має бути числом.")
        return

    if logic_update_record(records, rec_id, {"is_returned": True}) == 0:
        save_data(records)
        print(" Успіх: Статус змінено на 'Повернуто'.")
    else:
        print(" Помилка: Запис не знайдено.")

def ui_delete_loan():
    print("\n--- Видалення запису (0 для відміни) ---")
    records = load_data()
    try:
        id_str = input(" ID запису для видалення: ").strip()
        if id_str == "0": return
        rec_id = int(id_str)
    except ValueError:
        print(" Помилка: введіть ціле число.")
        return

    if logic_delete_record(records, rec_id) == 0:
        save_data(records)
        print(f" Успіх: Запис #{rec_id} видалено.")
    else:
        print(" Помилка: Запис не знайдено.")

def ui_import_file():
    print("\n--- Імпорт з файлу JSON (0 для відміни) ---")
    filepath = input(" Введіть шлях до файлу (напр., test_import.json): ").strip()
    if filepath == "0": return
    
    records = load_data()
    status = logic_import_json(records, filepath)
    
    if status == 0:
        save_data(records)
        print(" Успіх: Дані імпортовано!")
    elif status == 1:
        print(" Помилка: Файл не знайдено.")
    elif status == 2:
        print(" Помилка: Неправильний формат файлу.")

def ui_show_balance():
    print("\n--- Баланс (0 для відміни) ---")
    person = input(" Для кого рахуємо баланс? (напр. 'Я'): ").strip()
    if person == "0": return
    
    records = load_data()
    
    person_lower = person.lower()
    
    # Використовуємо .get() щоб програма не ламалась через відсутні поля
    owed_to_person = sum(r.get("amount", 0) for r in records if r.get("creditor", "").lower() == person_lower and not r.get("is_returned", False))
    person_owes = sum(r.get("amount", 0) for r in records if r.get("debtor", "").lower() == person_lower and not r.get("is_returned", False))
    
    print(f"\n Особі '{person}' винні: {owed_to_person:.2f} грн")
    print(f" Особа '{person}' винна:  {person_owes:.2f} грн")
    print("-" * 35)
    print(f" Чистий баланс:          {round(owed_to_person - person_owes, 2):.2f} грн")

# --- Головне меню ---
def menu():
    actions = {
        "1": ui_add_loan,
        "2": ui_show_all,
        "3": ui_edit_loan,
        "4": ui_mark_returned,
        "5": ui_show_balance,
        "6": ui_import_file,
        "7": ui_delete_loan,
    }
    
    while True:
        print("\n" + "="*55)
        print(" ПРО-Облік позик (Loan Tracker) ")
        print("="*55)
        print(" 1. Додати позику")
        print(" 2. Переглянути записи (всі або пошук)")
        print(" 3. Редагувати запис")
        print(" 4. Позначити як повернуте")
        print(" 5. Показати баланс конкретної особи")
        print(" 6. Імпортувати записи з JSON-файлу")
        print(" 7. Видалити запис")
        print(" 0. Вийти")
        
        choice = input("\n Ваш вибір: ").strip()
        
        if choice == "0":
            print(" До побачення!")
            break
            
        action = actions.get(choice)
        if action:
            action()
        else:
            print(" Невідома команда. Спробуйте ще раз.")

if __name__ == "__main__":
    menu()