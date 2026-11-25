import tkinter as tk
from tkinter import ttk

def window_auth():
    root = tk.Tk()
    root.title("ХимчисткаПро — окно авторизации")
    root.geometry("420x380")
    root.configure(bg="#faf5f7")
    tk.Label(root, text="Вход в систему", font=("Segoe UI", 16, "bold"), bg="#faf5f7").pack(pady=(20, 5))
    tk.Label(root, text="Введите данные для доступа", font=("Segoe UI", 10), bg="#faf5f7", fg="#666").pack()
    frm = tk.Frame(root, bg="#faf5f7"); frm.pack(pady=20, padx=40, fill="x")
    tk.Label(frm, text="Логин", bg="#faf5f7", anchor="w").pack(fill="x")
    tk.Entry(frm, font=("Segoe UI", 11), relief="solid", bd=1).pack(fill="x", ipady=4, pady=(0, 10))
    tk.Label(frm, text="Пароль", bg="#faf5f7", anchor="w").pack(fill="x")
    tk.Entry(frm, font=("Segoe UI", 11), relief="solid", bd=1, show="•").pack(fill="x", ipady=4, pady=(0, 10))
    tk.Label(frm, text="Роль:", bg="#faf5f7", anchor="w").pack(fill="x")
    ttk.Combobox(frm, values=["Администратор", "Кассир", "Технолог", "Кладовщик"], state="readonly").pack(fill="x", pady=(0, 15))
    tk.Button(root, text="Войти", bg="#e81a8b", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", padx=30, pady=8).pack(pady=10)
    tk.Label(root, text="● Статус сервера: Онлайн    Версия: 2.4.1", bg="#faf5f7", fg="#28a745", font=("Segoe UI", 9)).pack(side="bottom", pady=10)
    root.mainloop()

def window_orders():
    root = tk.Tk()
    root.title("ХимчисткаПро — список заказов")
    root.geometry("900x520")
    root.configure(bg="#faf5f7")
    tk.Label(root, text="Список заказов", font=("Segoe UI", 18, "bold"), bg="#faf5f7").pack(pady=10)
    bar = tk.Frame(root, bg="#faf5f7"); bar.pack(fill="x", padx=20)
    tk.Entry(bar, font=("Segoe UI", 11), relief="solid", bd=1, width=30).pack(side="left", padx=(0, 10))
    ttk.Combobox(bar, values=["Все статусы", "принят", "в химчистке", "на обработке", "готов к выдаче", "выдан"], state="readonly", width=25).pack(side="left")
    cols = ("№", "Клиент", "Телефон", "Вещей", "Сумма", "Статус")
    data = [
        ("1042", "Иванов А.А.", "+7 (900) 123-45-67", "3", "4500 ₽", "на обработке"),
        ("1043", "Петрова М.И.", "+7 (911) 234-56-78", "5", "7200 ₽", "готов к выдаче"),
        ("1044", "Сидоров В.П.", "+7 (922) 345-67-89", "1", "1200 ₽", "выдан"),
        ("1045", "Кузнецова Е.С.", "+7 (933) 456-78-90", "4", "5600 ₽", "принят"),
        ("1046", "Смирнов Д.К.", "+7 (944) 567-89-01", "2", "3100 ₽", "в химчистке"),
    ]
    tree = ttk.Treeview(root, columns=cols, show="headings", height=10)
    for c in cols: tree.heading(c, text=c)
    tree.column("№", width=60, anchor="center"); tree.column("Клиент", width=160)
    tree.column("Телефон", width=180); tree.column("Вещей", width=70, anchor="center")
    tree.column("Сумма", width=100, anchor="e"); tree.column("Статус", width=160, anchor="center")
    tree.pack(fill="both", expand=True, padx=20, pady=15)
    for r in data: tree.insert("", "end", values=r)
    btns = tk.Frame(root, bg="#faf5f7"); btns.pack(pady=10)
    tk.Button(btns, text="+ Новый заказ", bg="#e81a8b", fg="white", relief="flat", padx=20, pady=6).pack(side="left", padx=5)
    tk.Button(btns, text="✓ Выдать заказ", bg="#e81a8b", fg="white", relief="flat", padx=20, pady=6).pack(side="left", padx=5)
    root.mainloop()

def window_accept_success():
    root = tk.Tk()
    root.title("ХимчисткаПро — приём заказа (тестирование)")
    root.geometry("500x420")
    root.configure(bg="#faf5f7")
    tk.Label(root, text="Приём заказа", font=("Segoe UI", 16, "bold"), bg="#faf5f7").pack(pady=(15, 10))
    frm = tk.Frame(root, bg="#faf5f7"); frm.pack(padx=40, fill="x")
    for label, value in [("Клиент:", "Иванова Мария Петровна"), ("Телефон:", "+7 (912) 345-67-89"),
                         ("Тип вещи:", "Пальто"), ("Материал:", "Шерсть")]:
        tk.Label(frm, text=label, bg="#faf5f7", anchor="w").pack(fill="x")
        e = tk.Entry(frm, font=("Segoe UI", 11), relief="solid", bd=1); e.pack(fill="x", ipady=3, pady=(0, 8))
        e.insert(0, value)
    tk.Button(root, text="Оформить приём", bg="#e81a8b", fg="white", relief="flat", padx=20, pady=6).pack(pady=10)
    ok = tk.Label(root, text="✓  Заказ принят", bg="#e8f5e9", fg="#2e7d32", font=("Segoe UI", 12, "bold"), relief="solid", bd=1, padx=20, pady=8)
    ok.pack(pady=10, padx=40, fill="x")
    root.mainloop()

def window_issue_error():
    root = tk.Tk()
    root.title("ХимчисткаПро — выдача заказа (ошибка)")
    root.geometry("500x400")
    root.configure(bg="#faf5f7")
    tk.Label(root, text="Оформление выдачи", font=("Segoe UI", 16, "bold"), bg="#faf5f7").pack(pady=(15, 10))
    frm = tk.Frame(root, bg="#faf5f7"); frm.pack(padx=40, fill="x")
    for label, value in [("Заказ:", "№D4E5F6 - Петров А.А. (в химчистке)"),
                         ("ФИО клиента:", "Петров Алексей Андреевич"),
                         ("Телефон:", "+7 (903) 111-22-33"),
                         ("Сумма к оплате:", "450.00 руб.")]:
        tk.Label(frm, text=label, bg="#faf5f7", anchor="w").pack(fill="x")
        e = tk.Entry(frm, font=("Segoe UI", 11), relief="solid", bd=1); e.pack(fill="x", ipady=3, pady=(0, 8))
        e.insert(0, value)
    tk.Button(root, text="Оформить выдачу", bg="#e81a8b", fg="white", relief="flat", padx=20, pady=6).pack(pady=8)
    err = tk.Label(root, text="✗  Заказ ещё не готов к выдаче", bg="#fdecea", fg="#c62828", font=("Segoe UI", 12, "bold"), relief="solid", bd=1, padx=20, pady=8)
    err.pack(pady=10, padx=40, fill="x")
    root.mainloop()

# Запуск всех окон по очереди (для скриншотов)
if __name__ == "__main__":
    window_auth()       # скриншот 1
    window_orders()     # скриншот 2
    window_accept_success()  # скриншот 3
    window_issue_error()     # скриншот 4