"""
Окно оформления заказа ИС «ХимчисткаПро» (светлая розово-жёлтая тема).
Функционал:
- Привязка клиента (поиск по телефону)
- Добавление вещей (выбор из тарифов, количество)
- Генерация штрих-кодов
- Печать документов (квитанции)
Запуск: python order_window.py
"""
import tkinter as tk
from tkinter import ttk, messagebox
import uuid
from datetime import datetime

# ============================= ПАЛИТРА (из auth_mockup.py) =============================
BG_WINDOW    = "#FFF3F6"   # фон окна — очень светлый розовый
BG_CARD      = "#FFFFFF"   # фон карточки с полями — белый
HEADER_BG    = "#FCE4EC"   # шапка окна — нежно-розовый
PINK_MAIN    = "#F48FB1"   # основной розовый
PINK_DARK    = "#EC5F8A"   # розовый для акцентов/рамок
YELLOW_MAIN  = "#FFD54F"   # основной жёлтый
YELLOW_DARK  = "#F5B915"   # жёлтый для акцентов
TEXT_DARK    = "#4A3B3F"   # тёмный текст
TEXT_MUTED   = "#9A8A8F"   # приглушённый текст
TEXT_BONUS   = "#2E7D32"   # зелёный для бонусов/суммы
FIELD_BG     = "#FFFFFF"

# ============================= СПРАВОЧНИК ТАРИФОВ =============================
TARIFFS = {
    "Рубашка (150 ₽)": {"id": 1, "price": 150},
    "Брюки (300 ₽)": {"id": 2, "price": 300},
    "Пальто (500 ₽)": {"id": 3, "price": 500},
    "Костюм-двойка (850 ₽)": {"id": 4, "price": 850},
    "Пятновыведение (200 ₽)": {"id": 5, "price": 200},
}

# ============================= ЗАГЛУШКА БД КЛИЕНТОВ =============================
MOCK_CLIENTS = {
    "+79001234567": {"name": "Иванов Иван Иванович", "bonus": 150},
    "+79119876543": {"name": "Петрова Мария Сергеевна", "bonus": 320},
}


class OrderWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ХимчисткаПро — оформление заказа")
        self.geometry("750x700")
        self.resizable(False, False)
        self.configure(bg=BG_WINDOW)

        # Состояние заказа
        self.current_client = None
        self.cart = []  # список добавленных вещей: [{"name": "...", "price": 150, "qty": 2}]
        self.order_barcodes = []

        self._build_ui()

    # ------------------------- ШАПКА ОКНА -------------------------
    def _build_ui(self):
        # Верхняя полоса с названием и «светофором» из кружков
        header = tk.Frame(self, bg=HEADER_BG, height=34)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="ХимчисткаПро — оформление заказа",
                 bg=HEADER_BG, fg=TEXT_DARK,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=12)
        dots = tk.Frame(header, bg=HEADER_BG)
        dots.pack(side="right", padx=12)
        for color in ("#FF5F57", "#FEBC2E", "#28C840"):
            cv = tk.Canvas(dots, width=14, height=14, bg=HEADER_BG,
                           highlightthickness=0)
            cv.create_oval(2, 2, 12, 12, fill=color, outline="")
            cv.pack(side="left", padx=3)

        # ------------------------- ТЕЛО ОКНА -------------------------
        body = tk.Frame(self, bg=BG_WINDOW)
        body.pack(fill="both", expand=True, padx=28, pady=22)

        tk.Label(body, text="Новый заказ", bg=BG_WINDOW, fg=TEXT_DARK,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w")
        tk.Label(body, text="Заполните данные клиента и состав заказа",
                 bg=BG_WINDOW, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 16))

        # === КАРТОЧКА 1: КЛИЕНТ ===
        card_client = tk.Frame(body, bg=BG_CARD, highlightbackground=PINK_DARK, highlightthickness=1)
        card_client.pack(fill="x", pady=(0, 16))
        inner_client = tk.Frame(card_client, bg=BG_CARD)
        inner_client.pack(fill="x", padx=18, pady=16)

        tk.Label(inner_client, text="Привязка клиента", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))

        # Поиск
        search_frame = tk.Frame(inner_client, bg=BG_CARD)
        search_frame.pack(fill="x", pady=(0, 10))
        
        self.client_search = tk.Entry(search_frame, font=("Segoe UI", 11),
                                      bg=FIELD_BG, fg=TEXT_DARK,
                                      relief="flat", highlightthickness=1,
                                      highlightbackground=PINK_MAIN,
                                      highlightcolor=YELLOW_DARK)
        self.client_search.insert(0, "+79001234567") # демо-данные
        self.client_search.pack(side="left", fill="x", expand=True, ipady=5)
        
        tk.Button(search_frame, text="Найти", command=self._find_client,
                  bg=PINK_MAIN, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground=PINK_DARK,
                  padx=15).pack(side="left", padx=(10, 0))

        # Информация о клиенте
        self.client_info_label = tk.Label(inner_client, text="Клиент не выбран",
                                          bg=BG_CARD, fg=TEXT_MUTED,
                                          font=("Segoe UI", 10), anchor="w")
        self.client_info_label.pack(fill="x", pady=(5, 0))

        # === КАРТОЧКА 2: ВЕЩИ ===
        card_items = tk.Frame(body, bg=BG_CARD, highlightbackground=PINK_DARK, highlightthickness=1)
        card_items.pack(fill="both", expand=True, pady=(0, 16))
        inner_items = tk.Frame(card_items, bg=BG_CARD)
        inner_items.pack(fill="both", expand=True, padx=18, pady=16)

        tk.Label(inner_items, text="Состав заказа", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))

        # Добавление вещи
        add_frame = tk.Frame(inner_items, bg=BG_CARD)
        add_frame.pack(fill="x", pady=(0, 10))

        self.item_combo = ttk.Combobox(add_frame, values=list(TARIFFS.keys()), state="readonly",
                                       font=("Segoe UI", 10), width=30)
        self.item_combo.current(0)
        self.item_combo.pack(side="left", padx=(0, 10))

        self.qty_entry = tk.Entry(add_frame, font=("Segoe UI", 11), width=5,
                                  bg=FIELD_BG, fg=TEXT_DARK,
                                  relief="flat", highlightthickness=1,
                                  highlightbackground=PINK_MAIN)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(side="left", padx=(0, 10), ipady=4)

        tk.Button(add_frame, text="+ Добавить", command=self._add_item,
                  bg=YELLOW_MAIN, fg=TEXT_DARK, relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground=YELLOW_DARK,
                  padx=15).pack(side="left")

        # Таблица вещей (Treeview)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Pink.Treeview", background=BG_CARD, foreground=TEXT_DARK,
                        fieldbackground=BG_CARD, rowheight=28, font=("Segoe UI", 10))
        style.configure("Pink.Treeview.Heading", background=HEADER_BG, foreground=TEXT_DARK,
                        font=("Segoe UI", 10, "bold"))

        columns = ("name", "qty", "price", "total")
        self.tree = ttk.Treeview(inner_items, columns=columns, show="headings", style="Pink.Treeview")
        self.tree.heading("name", text="Наименование")
        self.tree.heading("qty", text="Кол-во")
        self.tree.heading("price", text="Цена")
        self.tree.heading("total", text="Сумма")
        
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("qty", width=60, anchor="center")
        self.tree.column("price", width=80, anchor="e")
        self.tree.column("total", width=100, anchor="e")
        
        self.tree.pack(fill="both", expand=True, pady=(5, 0))

        # === КАРТОЧКА 3: ИТОГО И ДЕЙСТВИЯ ===
        card_footer = tk.Frame(body, bg=BG_CARD, highlightbackground=PINK_DARK, highlightthickness=1)
        card_footer.pack(fill="x", pady=(0, 16))
        inner_footer = tk.Frame(card_footer, bg=BG_CARD)
        inner_footer.pack(fill="x", padx=18, pady=16)

        # Сумма
        sum_frame = tk.Frame(inner_footer, bg=BG_CARD)
        sum_frame.pack(fill="x", pady=(0, 15))
        tk.Label(sum_frame, text="Итого к оплате:", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 12)).pack(side="left")
        self.total_label = tk.Label(sum_frame, text="0.00 ₽", bg=BG_CARD, fg=TEXT_BONUS,
                                    font=("Segoe UI", 14, "bold"))
        self.total_label.pack(side="right")

        # Кнопки действий
        btn_frame = tk.Frame(inner_footer, bg=BG_CARD)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="🖨 Печать квитанции", command=self._print_receipt,
                  bg=PINK_MAIN, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground=PINK_DARK,
                  padx=12, pady=6).pack(side="left", padx=(0, 8))

        tk.Button(btn_frame, text="🏷 Штрих-коды", command=self._generate_barcodes,
                  bg="#81D4FA", fg=TEXT_DARK, relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground="#4FC3F7",
                  padx=12, pady=6).pack(side="left", padx=(0, 8))

        tk.Button(btn_frame, text="✓ Оформить заказ", command=self._save_order,
                  bg=YELLOW_MAIN, fg=TEXT_DARK, relief="flat",
                  font=("Segoe UI", 11, "bold"), activebackground=YELLOW_DARK,
                  padx=20, pady=6).pack(side="right")

        self._update_total()

    # ------------------------- ЛОГИКА -------------------------

    def _find_client(self):
        phone = self.client_search.get().strip()
        if phone in MOCK_CLIENTS:
            self.current_client = {"phone": phone, **MOCK_CLIENTS[phone]}
            self.client_info_label.configure(
                text=f"✅ {self.current_client['name']} | Баланс бонусов: {self.current_client['bonus']}",
                fg=TEXT_BONUS
            )
        else:
            self.current_client = None
            self.client_info_label.configure(text="❌ Клиент не найден.", fg="#D32F2F")

    def _add_item(self):
        item_name = self.item_combo.get()
        if not item_name:
            messagebox.showwarning("Внимание", "Выберите вещь из списка.")
            return
        
        try:
            qty = int(self.qty_entry.get())
            if qty <= 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Внимание", "Количество должно быть целым положительным числом.")
            return

        price = TARIFFS[item_name]["price"]
        total = price * qty
        
        self.cart.append({"name": item_name, "qty": qty, "price": price, "total": total})
        self._refresh_cart()

    def _refresh_cart(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for item in self.cart:
            self.tree.insert("", "end", values=(item["name"], item["qty"], f"{item['price']} ₽", f"{item['total']} ₽"))
        self._update_total()

    def _update_total(self):
        total = sum(item["total"] for item in self.cart)
        self.total_label.configure(text=f"{total}.00 ₽")

    def _generate_barcodes(self):
        if not self.cart:
            messagebox.showwarning("Внимание", "Сначала добавьте вещи в заказ.")
            return
        
        self.order_barcodes = [f"BC-{str(uuid.uuid4())[:6].upper()}-{i+1}" for i in range(len(self.cart))]
        bc_text = "\n".join(self.order_barcodes)
        messagebox.showinfo("Штрих-коды сгенерированы", f"Уникальные бирки для заказа:\n\n{bc_text}")

    def _print_receipt(self):
        if not self.cart:
            messagebox.showwarning("Внимание", "Заказ пуст. Нечего печатать.")
            return
        if not self.current_client:
            messagebox.showwarning("Внимание", "Не выбран клиент. Привяжите клиента перед печатью.")
            return
            
        total = sum(item["total"] for item in self.cart)
        msg = (f"КВИТАНЦИЯ №{str(uuid.uuid4())[:6].upper()}\n"
               f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
               f"Клиент: {self.current_client['name']}\n"
               f"------------------------------\n"
               f"ИТОГО: {total}.00 ₽\n\n"
               f"[Отправлено на принтер]")
        messagebox.showinfo("Печать", msg)

    def _save_order(self):
        if not self.current_client:
            messagebox.showerror("Ошибка", "Необходимо привязать клиента!")
            return
        if not self.cart:
            messagebox.showerror("Ошибка", "Заказ не может быть пустым!")
            return
        if not self.order_barcodes:
            messagebox.showwarning("Внимание", "Рекомендуем сначала сгенерировать штрих-коды.")
            return

        messagebox.showinfo("Успех", f"Заказ успешно сохранён!\nКлиент: {self.current_client['name']}\nСумма: {self.total_label['text']}")
        # Очистка формы
        self.cart = []
        self.order_barcodes = []
        self._refresh_cart()


if __name__ == "__main__":
    OrderWindow().mainloop()