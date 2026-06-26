import json
import os
import csv
from datetime import datetime

# --- Ініціалізація кольорів (ANSI) ---
if os.name == 'nt':
    os.system("")

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

DATA_FILE = "data.json"

# --- Інструменти інтерфейсу ---
def clear():
    """Очищує термінал для ефекту 'живого' додатка."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    """Зупиняє програму до натискання Enter."""
    input(f"\n{YELLOW} ⏎ Натисніть Enter, щоб повернутися до меню...{RESET}")

# --- Робота з файлами ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(records):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

# --- Ядро логіки (цілочисельні коди) ---
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

# --- Універсальний рушій фільтрації та сортування ---
def get_filtered_sorted_records(records):
    print(f"\n {BOLD}[1/3] Що шукаємо? (0 для відміни){RESET}")
    print(" 1. Всі записи (без фільтру за особою)")
    print(" 2. Записи конкретної особи")
    print(" 3. Пошук за ключовим словом (розумний пошук)")
    c1 = input(f" {CYAN}❯ Ваш вибір:{RESET} ").strip()
    if c1 == "0": return None
    
    filtered = records.copy()
    
    if c1 == "2":
        person = input(f" {CYAN}❯ Введіть ім'я особи:{RESET} ").strip().lower()
        if person == "0": return None
        
        print(f"\n {BOLD}[2/3] Фільтр для '{person.title()}' (0 для відміни):{RESET}")
        print(" 1. Всі борги, пов'язані з цією особою")
        print(" 2. Тільки борги, де особа дала гроші (Кредитор)")
        print(" 3. Тільки борги, де особа взяла гроші (Боржник)")
        c2 = input(f" {CYAN}❯ Ваш вибір:{RESET} ").strip()
        if c2 == "0": return None
        
        if c2 == "1":
            filtered = [r for r in filtered if str(r.get("creditor", "")).lower() == person or str(r.get("debtor", "")).lower() == person]
        elif c2 == "2":
            filtered = [r for r in filtered if str(r.get("creditor", "")).lower() == person]
        elif c2 == "3":
            filtered = [r for r in filtered if str(r.get("debtor", "")).lower() == person]
            
    elif c1 == "3":
        keyword = input(f" {CYAN}❯ Введіть слово для пошуку:{RESET} ").strip().lower()
        if keyword == "0": return None
        
        # Розумний пошук: збираємо всі дані в один рядок і шукаємо збіг
        filtered = [r for r in filtered if keyword in f"{r.get('creditor', '')} {r.get('debtor', '')} {r.get('note', '')}".lower()]
        
        # Миттєва перевірка, щоб не ганяти користувача по меню, якщо нічого немає
        if not filtered:
            print(f"\n{RED} ✘ Записів із словом '{keyword}' не знайдено.{RESET}")
            return []
                    
        print(f"\n {BOLD}[2/3] Статус знайдених записів (0 для відміни):{RESET}")
        print(" 1. Всі знайдені записи")
        print(" 2. Тільки активні (не повернуті)")
        print(" 3. Тільки повернуті")
        c2 = input(f" {CYAN}❯ Ваш вибір:{RESET} ").strip()
        if c2 == "0": return None
        
        if c2 == "2":
            filtered = [r for r in filtered if not r.get("is_returned")]
        elif c2 == "3":
            filtered = [r for r in filtered if r.get("is_returned")]

    elif c1 == "1":
        print(f"\n {BOLD}[2/3] Загальний фільтр (0 для відміни):{RESET}")
        print(" 1. Всі записи")
        print(" 2. Тільки активні (не повернуті)")
        print(" 3. Тільки повернуті")
        c2 = input(f" {CYAN}❯ Ваш вибір:{RESET} ").strip()
        if c2 == "0": return None
        
        if c2 == "2":
            filtered = [r for r in filtered if not r.get("is_returned")]
        elif c2 == "3":
            filtered = [r for r in filtered if r.get("is_returned")]
    else:
        return None

    if not filtered:
        print(f"\n{RED} ✘ Записів за цими критеріями не знайдено.{RESET}")
        return []

    print(f"\n {BOLD}[3/3] Сортування (0 для відміни):{RESET}")
    print(" 1. За замовчуванням (ID)")
    print(" 2. За датою (найновіші ↓)")
    print(" 3. За датою (найстаріші ↑)")
    print(" 4. За сумою (від найбільшої ↓)")
    print(" 5. За сумою (від найменшої ↑)")
    s_choice = input(f" {CYAN}❯ Ваш вибір (Enter для 1):{RESET} ").strip()
    if s_choice == "0": return None

    if s_choice == "2": filtered.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)
    elif s_choice == "3": filtered.sort(key=lambda x: str(x.get("timestamp", "")))
    elif s_choice == "4": filtered.sort(key=lambda x: float(x.get("amount", 0.0)), reverse=True)
    elif s_choice == "5": filtered.sort(key=lambda x: float(x.get("amount", 0.0)))
    
    return filtered

# --- Інтерфейс користувача (CLI) ---
def print_records(records):
    if not records:
        print(f"\n{RED} ✘ Записів немає.{RESET}")
        return
    
    # Ідеально вирівняна ASCII таблиця (математично точні відступи)
    print(f"\n{CYAN}┌{'─'*4}┬{'─'*14}┬{'─'*14}┬{'─'*12}┬{'─'*12}┬{'─'*18}┬{'─'*18}┐{RESET}")
    print(f"{CYAN}│{RESET} {BOLD}{'ID':<2}{RESET} {CYAN}│{RESET} {BOLD}{'Кредитор':<12}{RESET} {CYAN}│{RESET} {BOLD}{'Боржник':<12}{RESET} {CYAN}│{RESET} {BOLD}{'Сума':>10}{RESET} {CYAN}│{RESET} {BOLD}{'Статус':<10}{RESET} {CYAN}│{RESET} {BOLD}{'Час':<16}{RESET} {CYAN}│{RESET} {BOLD}{'Примітка':<16}{RESET} {CYAN}│{RESET}")
    print(f"{CYAN}├{'─'*4}┼{'─'*14}┼{'─'*14}┼{'─'*12}┼{'─'*12}┼{'─'*18}┼{'─'*18}┤{RESET}")
    
    for r in records:
        r_id = str(r.get("id", "?"))[:2]
        creditor = str(r.get("creditor", "Невідомо"))[:12]
        debtor = str(r.get("debtor", "Невідомо"))[:12]
        amount = f"{float(r.get('amount', 0.0)):.2f}"[:10]
        
        is_returned = r.get("is_returned", False)
        status_text = "Повернуто" if is_returned else "Активний"
        status_color = GREEN if is_returned else RED
        
        timestamp = str(r.get("timestamp", "-"))[:16]
        note = str(r.get("note", ""))[:16]

        print(f"{CYAN}│{RESET} {r_id:<2} {CYAN}│{RESET} {creditor:<12} {CYAN}│{RESET} {debtor:<12} {CYAN}│{RESET} {amount:>10} {CYAN}│{RESET} {status_color}{status_text:<10}{RESET} {CYAN}│{RESET} {timestamp:<16} {CYAN}│{RESET} {note:<16} {CYAN}│{RESET}")
        
    print(f"{CYAN}└{'─'*4}┴{'─'*14}┴{'─'*14}┴{'─'*12}┴{'─'*12}┴{'─'*18}┴{'─'*18}┘{RESET}")

def ui_add_loan():
    print(f"\n{BOLD}--- Додавання нової позики (0 для відміни) ---{RESET}")
    creditor = input(f" Хто {GREEN}дав{RESET} гроші (Кредитор)? : ").strip()
    if creditor == "0": return
    
    debtor = input(f" Хто {RED}взяв{RESET} гроші (Боржник)? : ").strip()
    if debtor == "0": return
    
    if not creditor or not debtor:
        print(f"{RED} ✘ Помилка: імена не можуть бути порожніми.{RESET}")
        return

    try:
        amount_str = input(" Сума: ").strip()
        if amount_str == "0": return
        amount = float(amount_str)
        if amount <= 0:
            print(f"{RED} ✘ Помилка: сума має бути більшою за нуль.{RESET}")
            return
    except ValueError:
        print(f"{RED} ✘ Помилка: введіть коректне число.{RESET}")
        return

    note = input(" Примітка (необов'язково): ").strip()
    if note == "0": return

    time_str = input(" Дата/час (напр. 2026-06-22 14:30) або Enter для поточного: ").strip()
    if time_str == "0": return
    
    timestamp = time_str if time_str else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    records = load_data()
    if logic_add_record(records, creditor, debtor, amount, note, timestamp) == 0:
        save_data(records)
        print(f"{GREEN} ✔ Успіх: Запис додано!{RESET}")

def ui_show_all():
    print(f"\n{BOLD}--- Перегляд позик ---{RESET}")
    records = load_data()
    if not records:
        print(f"{YELLOW} Список порожній.{RESET}")
        return

    result = get_filtered_sorted_records(records)
    if result is None or not result: return     
    
    clear()
    print(f"\n{BOLD}--- Результат перегляду ---{RESET}")
    print_records(result)

    print(f"\n{CYAN}------------------------------------{RESET}")
    export_choice = input(f" Бажаєте експортувати цю таблицю у CSV файл? (1 - Так, Enter - Ні): ").strip()
    if export_choice == "1":
        ui_do_csv_export(result)

def ui_do_csv_export(result):
    filename = input(f"\n {CYAN}❯ Введіть назву файлу (напр. my_debts):{RESET} ").strip()
    if filename == "0" or not filename: return
    
    if not filename.endswith(".csv"):
        filename += ".csv"
        
    try:
        with open(filename, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Кредитор", "Боржник", "Сума", "Статус", "Час", "Примітка"])
            for r in result:
                status = "Повернуто" if r.get("is_returned", False) else "Активний"
                writer.writerow([
                    r.get("id", "?"), str(r.get("creditor", "")), str(r.get("debtor", "")), 
                    float(r.get("amount", 0.0)), status, str(r.get("timestamp", "")), str(r.get("note", ""))
                ])
        print(f"{GREEN} ✔ Успіх: {len(result)} записів експортовано у '{filename}'!{RESET}")
    except Exception as e:
        print(f"{RED} ✘ Помилка при записі: {e}{RESET}")

def ui_export_csv():
    print(f"\n{BOLD}--- Експорт у CSV ---{RESET}")
    records = load_data()
    if not records:
        print(f"{YELLOW} Немає даних для експорту.{RESET}")
        return
        
    result = get_filtered_sorted_records(records)
    if result: ui_do_csv_export(result)

def ui_export_json():
    print(f"\n{BOLD}--- Експорт у JSON ---{RESET}")
    records = load_data()
    if not records:
        print(f"{YELLOW} Немає даних для експорту.{RESET}")
        return
        
    result = get_filtered_sorted_records(records)
    if not result: return

    filename = input(f"\n {CYAN}❯ Введіть назву файлу (напр. backup):{RESET} ").strip()
    if filename == "0" or not filename: return
    
    if not filename.endswith(".json"):
        filename += ".json"
        
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"{GREEN} ✔ Успіх: {len(result)} записів експортовано у '{filename}'!{RESET}")
    except Exception as e:
        print(f"{RED} ✘ Помилка при записі: {e}{RESET}")

def ui_edit_loan():
    print(f"\n{BOLD}--- Редагування запису (0 для відміни) ---{RESET}")
    records = load_data()
    if not records:
        print(f"{YELLOW} Список порожній.{RESET}")
        return
        
    try:
        rec_id = int(input(f" {CYAN}❯ Введіть ID запису:{RESET} ").strip())
        if rec_id == 0: return
    except ValueError:
        print(f"{RED} ✘ Помилка: ID має бути числом.{RESET}")
        return

    current_record = next((r for r in records if r.get("id") == rec_id), None)
    if not current_record:
        print(f"{RED} ✘ Помилка: Запис не знайдено.{RESET}")
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
            print(f"{RED} ✘ Помилка: некоректна сума.{RESET}")
            return

    new_note = input(f" Примітка [{current_record.get('note', '')}]: ").strip()

    updates = {}
    if new_creditor: updates["creditor"] = new_creditor
    if new_debtor: updates["debtor"] = new_debtor
    if new_amount_str: updates["amount"] = new_amount
    if new_note: updates["note"] = new_note
    updates["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if logic_update_record(records, rec_id, updates) == 0:
        save_data(records)
        print(f"{GREEN} ✔ Успіх: Запис оновлено!{RESET}")

def ui_mark_returned():
    print(f"\n{BOLD}--- Позначити позику як повернуту ---{RESET}")
    records = load_data()
    
    try:
        rec_id = int(input(f" {CYAN}❯ Введіть ID позики (0 - відміна):{RESET} ").strip())
        if rec_id == 0: return
    except ValueError:
        print(f"{RED} ✘ Помилка: ID має бути числом.{RESET}")
        return

    if logic_update_record(records, rec_id, {"is_returned": True}) == 0:
        save_data(records)
        print(f"{GREEN} ✔ Успіх: Статус змінено на 'Повернуто'.{RESET}")
    else:
        print(f"{RED} ✘ Помилка: Запис не знайдено.{RESET}")

def ui_delete_loan():
    print(f"\n{BOLD}--- Видалення запису ---{RESET}")
    records = load_data()
    try:
        rec_id = int(input(f" {CYAN}❯ ID запису для видалення (0 - відміна):{RESET} ").strip())
        if rec_id == 0: return
    except ValueError:
        print(f"{RED} ✘ Помилка: введіть ціле число.{RESET}")
        return

    if logic_delete_record(records, rec_id) == 0:
        save_data(records)
        print(f"{GREEN} ✔ Успіх: Запис #{rec_id} видалено.{RESET}")
    else:
        print(f"{RED} ✘ Помилка: Запис не знайдено.{RESET}")

def ui_show_balance():
    print(f"\n{BOLD}--- Баланс ---{RESET}")
    person = input(f" {CYAN}❯ Для кого рахуємо баланс?:{RESET} ").strip()
    if person == "0" or not person: return
    
    records = load_data()
    p_low = person.lower()
    
    owed_to = sum(float(r.get("amount", 0)) for r in records if str(r.get("creditor", "")).lower() == p_low and not r.get("is_returned", False))
    owes = sum(float(r.get("amount", 0)) for r in records if str(r.get("debtor", "")).lower() == p_low and not r.get("is_returned", False))
    net = owed_to - owes
    
    # Вирівняний ASCII Блок балансу
    person_str = person.title()[:26]
    owed_str = f"{owed_to:.2f} грн"
    owes_str = f"{owes:.2f} грн"
    net_str = f"{net:.2f} грн"
    net_color = GREEN if net >= 0 else RED
    
    print(f"\n {CYAN}┌{'─'*40}┐{RESET}")
    print(f" {CYAN}│{RESET} {BOLD}Баланс для: {person_str:<28}{RESET}{CYAN}│{RESET}")
    print(f" {CYAN}├{'─'*40}┤{RESET}")
    print(f" {CYAN}│{RESET} {GREEN}Винні вам: {owed_str:>28}{RESET} {CYAN}│{RESET}")
    print(f" {CYAN}│{RESET} {RED}Ви винні:  {owes_str:>28}{RESET} {CYAN}│{RESET}")
    print(f" {CYAN}├{'─'*40}┤{RESET}")
    print(f" {CYAN}│{RESET} {BOLD}Чистий:    {RESET}{net_color}{net_str:>28}{RESET} {CYAN}│{RESET}")
    print(f" {CYAN}└{'─'*40}┘{RESET}")

# --- Головне меню ---
def menu():
    actions = {
        "1": ui_add_loan, "2": ui_show_all, "3": ui_edit_loan,
        "4": ui_mark_returned, "5": ui_show_balance, 
        "6": ui_export_csv, "7": ui_export_json, "8": ui_delete_loan
    }
    
    while True:
        clear()
        print(f"{CYAN}╔═════════════════════════════════════════════════════════╗{RESET}")
        print(f"{CYAN}║{RESET} {BOLD}{YELLOW}{'ПРО-Облік позик (Loan Tracker)'.center(55)}{RESET} {CYAN}║{RESET}")
        print(f"{CYAN}╠═════════════════════════════════════════════════════════╣{RESET}")
        print(f"{CYAN}║{RESET} {BOLD}1.{RESET} {'Додати позику':<52} {CYAN}║{RESET}")
        print(f"{CYAN}║{RESET} {BOLD}2.{RESET} {'Переглянути записи (Фільтри + Сортування)':<52} {CYAN}║{RESET}")
        print(f"{CYAN}║{RESET} {BOLD}3.{RESET} {'Редагувати запис':<52} {CYAN}║{RESET}")
        print(f"{CYAN}║{RESET} {BOLD}4.{RESET} {'Позначити як повернуте':<52} {CYAN}║{RESET}")
        print(f"{CYAN}║{RESET} {BOLD}5.{RESET} {'Показати баланс конкретної особи':<52} {CYAN}║{RESET}")
        print(f"{CYAN}║{RESET} {BOLD}6.{RESET} {'Експортувати в CSV':<52} {CYAN}║{RESET}")
        print(f"{CYAN}║{RESET} {BOLD}7.{RESET} {'Експортувати в JSON':<52} {CYAN}║{RESET}")
        print(f"{CYAN}║{RESET} {BOLD}8.{RESET} {'Видалити запис':<52} {CYAN}║{RESET}")
        print(f"{CYAN}║{RESET} {RED}0. Вийти{RESET}                                              {CYAN}║{RESET}")
        print(f"{CYAN}╚═════════════════════════════════════════════════════════╝{RESET}")
        
        choice = input(f"\n {CYAN}❯ Ваш вибір:{RESET} ").strip()
        
        if choice == "0":
            clear()
            print(f"{GREEN} До побачення!{RESET}")
            break
            
        action = actions.get(choice)
        if action:
            clear()
            action()
            pause()
        else:
            print(f"{RED} ✘ Невідома команда.{RESET}")
            pause()

if __name__ == "__main__":
    menu()