import json
import os
from datetime import date

DATA_FILE = "data.json"

# --- Робота з файлами ---

def load_data():
    """Завантажує записи з JSON-файлу. Якщо файл не існує — повертає порожній список."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(records):
    """Записує список записів у JSON-файл."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

# --- Допоміжні функції ---

def next_id(records):
    """Генерує наступний унікальний ідентифікатор."""
    if not records:
        return 1
    return max(r["id"] for r in records) + 1

def print_records(records):
    """Виводить список записів у вигляді форматованої таблиці."""
    if not records:
        print(" Записів немає.")
        return
    
    print(f" {'ID':<4} {'Особа':<15} {'Тип боргу':<12} {'Сума':>10} {'Статус':<12} {'Дата':<12} {'Примітка'}")
    print(" " + "-" * 85)
    for r in records:
        # Переклад системних значень для зручного читання
        l_type = "Мені винні" if r['type'] == 'owe_me' else "Я винен"
        status = "Повернуто" if r['is_returned'] else "Активний"
        
        print(f" {r['id']:<4} {r['person']:<15} {l_type:<12} {r['amount']:>10.2f} {status:<12} {r['date']:<12} {r['note']}")

# --- Основна логіка ---

def add_loan():
    """Запитує дані у користувача і додає новий запис про позику."""
    print("\n--- Додавання нової позики ---")
    person = input(" Ім'я людини: ").strip()
    if not person:
        print(" Помилка: ім'я не може бути порожнім.")
        return

    print(" Тип боргу:")
    print(" 1 - Мені винні")
    print(" 2 - Я винен")
    choice = input(" Ваш вибір (1 або 2): ").strip()
    
    if choice == "1":
        loan_type = "owe_me"
    elif choice == "2":
        loan_type = "i_owe"
    else:
        print(" Помилка: невідомий вибір типу.")
        return

    try:
        amount = float(input(" Сума: ").strip())
        if amount <= 0:
            print(" Помилка: сума має бути більшою за нуль.")
            return
    except ValueError:
        print(" Помилка: введіть коректне число (наприклад, 150 або 150.50).")
        return

    date_str = input(f" Дата (Enter = {date.today()}): ").strip()
    if not date_str:
        date_str = str(date.today())

    note = input(" Примітка (необов'язково): ").strip()

    records = load_data()
    
    records.append({
        "id": next_id(records),
        "person": person,
        "type": loan_type,
        "amount": round(amount, 2),
        "date": date_str,
        "is_returned": False,
        "note": note
    })
    
    save_data(records)
    print(" Успіх: Запис про позику додано!")

def show_all():
    """Виводить усі записи."""
    print("\n--- Всі позики ---")
    records = load_data()
    print_records(records)

def mark_returned():
    """Змінює статус позики на 'Повернуто'."""
    print("\n--- Позначити позику як повернуту ---")
    records = load_data()
    if not records:
        print(" Список позик порожній.")
        return
        
    print_records(records)
    
    try:
        rec_id = int(input("\n Введіть ID позики, яку повернули: ").strip())
    except ValueError:
        print(" Помилка: ID має бути цілим числом.")
        return

    found = False
    for r in records:
        if r["id"] == rec_id:
            if r["is_returned"]:
                print(" Ця позика вже була позначена як повернута.")
            else:
                r["is_returned"] = True
                print(f" Успіх: Статус позики #{rec_id} змінено на 'Повернуто'.")
            found = True
            break
            
    if not found:
        print(" Помилка: Позику з таким ID не знайдено.")
    else:
        save_data(records)

def show_balance():
    """Підраховує і виводить загальний баланс активних (не повернутих) боргів."""
    print("\n--- Баланс боргів ---")
    records = load_data()
    
    # Рахуємо тільки активні (не повернуті) борги
    owe_me_total = sum(r["amount"] for r in records if r["type"] == "owe_me" and not r["is_returned"])
    i_owe_total = sum(r["amount"] for r in records if r["type"] == "i_owe" and not r["is_returned"])
    
    balance = round(owe_me_total - i_owe_total, 2)
    
    print(f" Активні борги мені: {owe_me_total:.2f} грн")
    print(f" Мої активні борги:  {i_owe_total:.2f} грн")
    print("-" * 30)
    print(f" Загальний баланс:   {balance:.2f} грн")

def delete_loan():
    """Видаляє запис за ідентифікатором."""
    print("\n--- Видалення запису ---")
    records = load_data()
    if not records:
        print(" Список позик порожній.")
        return
        
    try:
        rec_id = int(input(" ID запису для видалення: ").strip())
    except ValueError:
        print(" Помилка: введіть ціле число.")
        return

    new_records = [r for r in records if r["id"] != rec_id]

    if len(new_records) == len(records):
        print(" Помилка: Запис не знайдено.")
        return

    save_data(new_records)
    print(f" Успіх: Запис #{rec_id} видалено.")

# --- Меню ---

def menu():
    """Головний цикл програми з текстовим меню."""
    actions = {
        "1": add_loan,
        "2": show_all,
        "3": mark_returned,
        "4": show_balance,
        "5": delete_loan,
    }
    
    while True:
        print("\n" + "="*45)
        print(" Облік позик")
        print("="*45)
        print(" 1. Додати позику")
        print(" 2. Переглянути всі записи")
        print(" 3. Позначити як повернуте")
        print(" 4. Показати загальний баланс")
        print(" 5. Видалити запис")
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