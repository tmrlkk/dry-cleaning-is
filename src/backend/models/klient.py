"""
Окно работы с клиентами ИС «ХимчисткаПро» (светлая розово-жёлтая тема).
Функционал:
- CRUD-операции с карточками клиентов
- Поиск по телефону/ФИО
- Учёт бонусов (начисление/списание)
Запуск: python client_window.py
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ============================= ПАЛИТРА =============================
BG_WINDOW    = "#FFF3F6"
BG_CARD      = "#FFFFFF"
HEADER_BG    = "#FCE4EC"
PINK_MAIN    = "#F48FB1"
PINK_DARK    = "#EC5F8A"
YELLOW_MAIN  = "#FFD54F"
YELLOW_DARK  = "#F5B915"
TEXT_DARK    = "#4A3B3F"
TEXT_MUTED   = "#9A8A8F"
TEXT_BONUS   = "#2E7D32"
FIELD_BG     = "#FFFFFF"
ROW_SELECTED = "#FFF9C4"


class Client:
    """Модель клиента"""
    def __init__(self, client_id, full_name, phone, email, bonus_balance=0):
        self.client_id = client_id
        self.full_name = full_name
        self.phone = phone
        self.email = email
        self.bonus_balance = bonus_balance
        self.created_at = datetime.now().strftime("%d.%m.%Y")


class MockClientRepository:
    """Заглушка репозитория клиентов"""
    def __init__(self):
        self.clients = [
            Client(1, "Иванов Иван Иванович", "+7 (900) 123-45-67", "ivanov@mail.ru", 150),
            Client(2, "Петрова Мария Сергеевна", "+7 (911) 234-56-78", "petrova@mail.ru", 320),
            Client(3, "Сидоров Алексей Петрович", "+7 (922) 345-67-89", "sidorov@mail.ru", 0),
            Client(4, "Кузнецова Елена Дмитриевна", "+7 (933) 456-78-90", "kuznetsova@mail.ru", 85),
        ]
        self.next_id = 5

    def get_all(self):
        return self.clients

    def search(self, query):
        query = query.lower().strip()
        if not query:
            return self.clients
        return [c for c in self.clients 
                if query in c.full_name.lower() or query in c.phone.replace(" ", "").replace("-", "")]

    def add(self, client):
        client.client_id = self.next_id
        self.next_id += 1
        self.clients.append(client)
        return client

    def update(self, client):
        for i, c in enumerate(self.clients):
            if c.client_id == client.client_id:
                self.clients[i] = client
                return True
        return False

    def delete(self, client_id):
        self.clients = [c for c in self.clients if c.client_id != client_id]

    def accrue_bonus(self, client_id, amount):
        for c in self.clients:
            if c.client_id == client_id:
                c.bonus_balance += amount
                return c.bonus_balance
        return None

    def write_off_bonus(self, client_id, amount):
        for c in self.clients:
            if c.client_id == client_id:
                if c.bonus_balance >= amount:
                    c.bonus_balance -= amount
                    return c.bonus_balance
                else:
                    return None
        return None


class ClientEditDialog(tk.Toplevel):
    """Диалог добавления/редактирования клиента"""
    def __init__(self, parent, client=None):
        super().__init__(parent)
        self.title("Добавление клиента" if client is None else "Редактирование клиента")
        self.geometry("420x480")
        self.resizable(False, False)
        self.configure(bg=BG_WINDOW)
        self.transient(parent)
        self.grab_set()
        
        self.client = client
        self.result = None
        
        self._build_ui()
        
        if client:
            self.name_entry.insert(0, client.full_name)
            self.phone_entry.insert(0, client.phone)
            self.email_entry.insert(0, client.email)
        
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _build_ui(self):
        header = tk.Frame(self, bg=HEADER_BG, height=34)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=self.title(), bg=HEADER_BG, fg=TEXT_DARK,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=12)
        
        body = tk.Frame(self, bg=BG_WINDOW)
        body.pack(fill="both", expand=True, padx=24, pady=20)
        
        card = tk.Frame(body, bg=BG_CARD, highlightbackground=PINK_DARK,
                        highlightthickness=1)
        card.pack(fill="x", pady=(0, 16))
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill="x", padx=18, pady=16)
        
        tk.Label(inner, text="ФИО", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 10)).pack(anchor="w")
        self.name_entry = tk.Entry(inner, font=("Segoe UI", 11),
                                    bg=FIELD_BG, fg=TEXT_DARK,
                                    relief="flat", highlightthickness=1,
                                    highlightbackground=PINK_MAIN,
                                    highlightcolor=YELLOW_DARK)
        self.name_entry.pack(fill="x", ipady=5, pady=(2, 12))
        
        tk.Label(inner, text="Телефон", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 10)).pack(anchor="w")
        self.phone_entry = tk.Entry(inner, font=("Segoe UI", 11),
                                     bg=FIELD_BG, fg=TEXT_DARK,
                                     relief="flat", highlightthickness=1,
                                     highlightbackground=PINK_MAIN,
                                     highlightcolor=YELLOW_DARK)
        self.phone_entry.pack(fill="x", ipady=5, pady=(2, 12))
        
        tk.Label(inner, text="Email", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 10)).pack(anchor="w")
        self.email_entry = tk.Entry(inner, font=("Segoe UI", 11),
                                     bg=FIELD_BG, fg=TEXT_DARK,
                                     relief="flat", highlightthickness=1,
                                     highlightbackground=PINK_MAIN,
                                     highlightcolor=YELLOW_DARK)
        self.email_entry.pack(fill="x", ipady=5, pady=(2, 4))
        
        btn_frame = tk.Frame(body, bg=BG_WINDOW)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(btn_frame, text="Сохранить", command=self._save,
                  bg=YELLOW_MAIN, fg=TEXT_DARK, relief="flat",
                  font=("Segoe UI", 11, "bold"), activebackground=YELLOW_DARK,
                  pady=8).pack(side="left", expand=True, fill="x", padx=(0, 6))
        
        tk.Button(btn_frame, text="Отмена", command=self._cancel,
                  bg=PINK_MAIN, fg="white", relief="flat",
                  font=("Segoe UI", 11, "bold"), activebackground=PINK_DARK,
                  pady=8).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _save(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not name or not phone:
            messagebox.showwarning("Внимание", "Заполните ФИО и телефон.")
            return
        
        if self.client:
            self.client.full_name = name
            self.client.phone = phone
            self.client.email = email
        else:
            self.client = Client(0, name, phone, email)
        
        self.result = self.client
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


class BonusDialog(tk.Toplevel):
    """Диалог начисления/списания бонусов"""
    def __init__(self, parent, client, mode="accrue"):
        super().__init__(parent)
        self.title("Начисление бонусов" if mode == "accrue" else "Списание бонусов")
        self.geometry("380x320")
        self.resizable(False, False)
        self.configure(bg=BG_WINDOW)
        self.transient(parent)
        self.grab_set()
        
        self.client = client
        self.mode = mode
        self.result = None
        
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _build_ui(self):
        header = tk.Frame(self, bg=HEADER_BG, height=34)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=self.title(), bg=HEADER_BG, fg=TEXT_DARK,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=12)
        
        body = tk.Frame(self, bg=BG_WINDOW)
        body.pack(fill="both", expand=True, padx=24, pady=20)
        
        tk.Label(body, text=f"Клиент: {self.client.full_name}",
                 bg=BG_WINDOW, fg=TEXT_DARK, font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 8))
        
        tk.Label(body, text=f"Текущий баланс: {self.client.bonus_balance} бонусов",
                 bg=BG_WINDOW, fg=TEXT_BONUS, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 16))
        
        card = tk.Frame(body, bg=BG_CARD, highlightbackground=PINK_DARK,
                        highlightthickness=1)
        card.pack(fill="x", pady=(0, 16))
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill="x", padx=18, pady=16)
        
        tk.Label(inner, text="Количество бонусов", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 10)).pack(anchor="w")
        self.amount_entry = tk.Entry(inner, font=("Segoe UI", 11),
                                      bg=FIELD_BG, fg=TEXT_DARK,
                                      relief="flat", highlightthickness=1,
                                      highlightbackground=PINK_MAIN,
                                      highlightcolor=YELLOW_DARK)
        self.amount_entry.pack(fill="x", ipady=5, pady=(2, 4))
        
        btn_frame = tk.Frame(body, bg=BG_WINDOW)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        btn_text = "Начислить" if self.mode == "accrue" else "Списать"
        btn_color = YELLOW_MAIN if self.mode == "accrue" else PINK_MAIN
        btn_active = YELLOW_DARK if self.mode == "accrue" else PINK_DARK
        
        tk.Button(btn_frame, text=btn_text, command=self._confirm,
                  bg=btn_color, fg=TEXT_DARK if self.mode == "accrue" else "white",
                  relief="flat", font=("Segoe UI", 11, "bold"),
                  activebackground=btn_active, pady=8).pack(side="left", expand=True, fill="x", padx=(0, 6))
        
        tk.Button(btn_frame, text="Отмена", command=self._cancel,
                  bg=PINK_MAIN, fg="white", relief="flat",
                  font=("Segoe UI", 11, "bold"), activebackground=PINK_DARK,
                  pady=8).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _confirm(self):
        try:
            amount = int(self.amount_entry.get().strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Внимание", "Введите положительное число.")
            return
        
        if self.mode == "accrue":
            self.result = amount
        else:
            if amount > self.client.bonus_balance:
                messagebox.showerror("Ошибка", "Недостаточно бонусов на балансе.")
                return
            self.result = -amount
        
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


class ClientWindow(tk.Tk):
    """Главное окно работы с клиентами"""
    def __init__(self):
        super().__init__()
        self.title("ХимчисткаПро — работа с клиентами")
        self.geometry("900x650")
        self.configure(bg=BG_WINDOW)
        
        self.repo = MockClientRepository()
        self.current_clients = self.repo.get_all()
        
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        # Шапка
        header = tk.Frame(self, bg=HEADER_BG, height=34)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="ХимчисткаПро — работа с клиентами",
                 bg=HEADER_BG, fg=TEXT_DARK,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=12)
        
        dots = tk.Frame(header, bg=HEADER_BG)
        dots.pack(side="right", padx=12)
        for color in ("#FF5F57", "#FEBC2E", "#28C840"):
            cv = tk.Canvas(dots, width=14, height=14, bg=HEADER_BG,
                           highlightthickness=0)
            cv.create_oval(2, 2, 12, 12, fill=color, outline="")
            cv.pack(side="left", padx=3)
        
        # Тело
        body = tk.Frame(self, bg=BG_WINDOW)
        body.pack(fill="both", expand=True, padx=20, pady=16)
        
        # Панель поиска
        search_frame = tk.Frame(body, bg=BG_WINDOW)
        search_frame.pack(fill="x", pady=(0, 12))
        
        tk.Label(search_frame, text="Поиск:", bg=BG_WINDOW, fg=TEXT_DARK,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        
        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 11),
                                      bg=FIELD_BG, fg=TEXT_DARK,
                                      relief="flat", highlightthickness=1,
                                      highlightbackground=PINK_MAIN,
                                      highlightcolor=YELLOW_DARK, width=40)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 12), ipady=4)
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search())
        
        # Кнопки действий
        btn_frame = tk.Frame(body, bg=BG_WINDOW)
        btn_frame.pack(fill="x", pady=(0, 12))
        
        tk.Button(btn_frame, text="+ Добавить клиента", command=self._add_client,
                  bg=YELLOW_MAIN, fg=TEXT_DARK, relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground=YELLOW_DARK,
                  padx=16, pady=6).pack(side="left", padx=(0, 8))
        
        tk.Button(btn_frame, text="✎ Редактировать", command=self._edit_client,
                  bg=PINK_MAIN, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground=PINK_DARK,
                  padx=16, pady=6).pack(side="left", padx=(0, 8))
        
        tk.Button(btn_frame, text="✕ Удалить", command=self._delete_client,
                  bg="#FF6B6B", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground="#FF5252",
                  padx=16, pady=6).pack(side="left", padx=(0, 8))
        
        tk.Button(btn_frame, text="+ Начислить бонусы", command=lambda: self._bonus("accrue"),
                  bg="#4CAF50", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground="#45A049",
                  padx=16, pady=6).pack(side="left", padx=(0, 8))
        
        tk.Button(btn_frame, text="- Списать бонусы", command=lambda: self._bonus("write_off"),
                  bg="#FF9800", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground="#F57C00",
                  padx=16, pady=6).pack(side="left")
        
        # Таблица клиентов
        table_frame = tk.Frame(body, bg=BG_CARD, highlightbackground=PINK_DARK,
                               highlightthickness=1)
        table_frame.pack(fill="both", expand=True)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=BG_CARD,
                        foreground=TEXT_DARK,
                        fieldbackground=BG_CARD,
                        rowheight=32,
                        font=("Segoe UI", 10))
        style.configure("Custom.Treeview.Heading",
                        background=HEADER_BG,
                        foreground=TEXT_DARK,
                        font=("Segoe UI", 10, "bold"))
        style.map("Custom.Treeview",
                  background=[("selected", ROW_SELECTED)])
        
        columns = ("id", "name", "phone", "email", "bonus")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                  style="Custom.Treeview")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="ФИО")
        self.tree.heading("phone", text="Телефон")
        self.tree.heading("email", text="Email")
        self.tree.heading("bonus", text="Бонусы")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("phone", width=150, anchor="center")
        self.tree.column("email", width=200, anchor="w")
        self.tree.column("bonus", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<Double-1>", lambda e: self._edit_client())
        
        # Статус-бар
        self.status_var = tk.StringVar(value="Готово")
        tk.Label(body, textvariable=self.status_var, bg=BG_WINDOW,
                 fg=TEXT_MUTED, font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=(8, 0))

    def _refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for client in self.current_clients:
            self.tree.insert("", "end", iid=client.client_id,
                           values=(client.client_id, client.full_name,
                                   client.phone, client.email,
                                   client.bonus_balance))
        
        self.status_var.set(f"Всего клиентов: {len(self.current_clients)}")

    def _on_search(self):
        query = self.search_entry.get()
        self.current_clients = self.repo.search(query)
        self._refresh_list()

    def _get_selected_client(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите клиента из списка.")
            return None
        client_id = int(selection[0])
        for c in self.repo.get_all():
            if c.client_id == client_id:
                return c
        return None

    def _add_client(self):
        dialog = ClientEditDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self.repo.add(dialog.result)
            self._on_search()
            messagebox.showinfo("Успех", "Клиент добавлен.")

    def _edit_client(self):
        client = self._get_selected_client()
        if not client:
            return
        dialog = ClientEditDialog(self, client)
        self.wait_window(dialog)
        if dialog.result:
            self.repo.update(dialog.result)
            self._on_search()
            messagebox.showinfo("Успех", "Данные клиента обновлены.")

    def _delete_client(self):
        client = self._get_selected_client()
        if not client:
            return
        if messagebox.askyesno("Подтверждение", 
                               f"Удалить клиента {client.full_name}?"):
            self.repo.delete(client.client_id)
            self._on_search()
            messagebox.showinfo("Успех", "Клиент удалён.")

    def _bonus(self, mode):
        client = self._get_selected_client()
        if not client:
            return
        dialog = BonusDialog(self, client, mode)
        self.wait_window(dialog)
        if dialog.result is not None:
            if mode == "accrue":
                new_balance = self.repo.accrue_bonus(client.client_id, dialog.result)
                messagebox.showinfo("Успех", 
                    f"Начислено {dialog.result} бонусов.\nНовый баланс: {new_balance}")
            else:
                new_balance = self.repo.write_off_bonus(client.client_id, abs(dialog.result))
                if new_balance is not None:
                    messagebox.showinfo("Успех", 
                        f"Списано {abs(dialog.result)} бонусов.\nНовый баланс: {new_balance}")
                else:
                    messagebox.showerror("Ошибка", "Недостаточно бонусов.")
            self._on_search()


if __name__ == "__main__":
    ClientWindow().mainloop()