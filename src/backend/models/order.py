"""
Окно оформления заказа ИС «ХимчисткаПро» (светлая розово-жёлтая тема).
Функционал:
- Привязка клиента (поиск по телефону)
- Добавление/удаление вещей (только позиции, БЕЗ встроенного расчёта суммы)
- Генерация штрих-кодов
- Печать документов (квитанции)
- Связь с calculator_window.py: кнопка «Открыть калькулятор» открывает
  CalculatorWindow как модальное окно, передаёт cart + client_id,
  получает обратно итоговую сумму.
Запуск: python order.py
(требуется calculator_window.py и calculator_module.py в той же папке)
"""
import tkinter as tk
from tkinter import ttk, messagebox
import uuid
from datetime import datetime

# --- Интеграция с модулем расчёта (общая бизнес-логика) ---
from calculator_module import OrderCalculator, MockTariffRepository, OrderItem

# --- Интеграция с окном калькулятора ---
try:
    from calculator_window import CalculatorWindow
    _CALC_WINDOW_AVAILABLE = True
except ImportError:
    CalculatorWindow = None
    _CALC_WINDOW_AVAILABLE = False

# ============================= ПАЛИТРА (как в auth_mockup.py) =============================
BG_WINDOW    = "#FFF3F6"
BG_CARD      = "#FFFFFF"
HEADER_BG    = "#FCE4EC"
PINK_MAIN    = "#F48FB1"
PINK_DARK    = "#EC5F8A"
YELLOW_MAIN  = "#FFD54F"
YELLOW_DARK  = "#F5B915"
TEXT_DARK    = "#4A3B3F"
TEXT_MUTED   = "#9A8A8F"
TEXT_TOTAL   = "#2E7D32"
FIELD_BG     = "#FFFFFF"

# ============================= СПРАВОЧНИК ТАРИФОВ =============================
TARIFFS = {
    "Рубашка": {"id": 1, "price": 150},
    "Брюки": {"id": 2, "price": 300},
    "Пальто": {"id": 3, "price": 500},
    "Костюм-двойка": {"id": 4, "price": 850},
    "Пятновыведение": {"id": 5, "price": 200},
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
        self.geometry("750x680")
        self.resizable(False, False)
        self.configure(bg=BG_WINDOW)

        # Состояние заказа (cart хранит ТОЛЬКО позиции, без сумм)
        self.current_client = None
        self.cart = []  # [{"name": "Рубашка", "qty": 2, "type_id": 1}]
        self.order_barcodes = []
        self.calculated_total = None  # сюда вернётся результат из CalculatorWindow

        # Общий калькулятор (используется для быстрого расчёта)
        self.calculator = OrderCalculator(MockTariffRepository())

        self._build_ui()

    # ------------------------- ШАПКА ОКНА -------------------------
    def _build_ui(self):
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

        body = tk.Frame(self, bg=BG_WINDOW)
        body.pack(fill="both", expand=True, padx=28, pady=22)

        tk.Label(body, text="Новый заказ", bg=BG_WINDOW, fg=TEXT_DARK,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w")
        tk.Label(body, text="Привяжите клиента, добавьте вещи, затем рассчитайте стоимость",
                 bg=BG_WINDOW, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 16))

        # === КАРТОЧКА 1: КЛИЕНТ ===
        card_client = self._make_card(body)
        tk.Label(card_client, text="Привязка клиента", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))

        search_frame = tk.Frame(card_client, bg=BG_CARD)
        search_frame.pack(fill="x", pady=(0, 10))

        self.client_search = tk.Entry(search_frame, font=("Segoe UI", 11),
                                      bg=FIELD_BG, fg=TEXT_DARK,
                                      relief="flat", highlightthickness=1,
                                      highlightbackground=PINK_MAIN,
                                      highlightcolor=YELLOW_DARK)
        self.client_search.insert(0, "+79001234567")
        self.client_search.pack(side="left", fill="x", expand=True, ipady=5)

        tk.Button(search_frame, text="Найти", command=self._find_client,
                  bg=PINK_MAIN, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground=PINK_DARK,
                  padx=15).pack(side="left", padx=(10, 0))

        self.client_info_label = tk.Label(card_client, text="Клиент не выбран",
                                          bg=BG_CARD, fg=TEXT_MUTED,
                                          font=("Segoe UI", 10), anchor="w")
        self.client_info_label.pack(fill="x", pady=(5, 0))

        # === КАРТОЧКА 2: СОСТАВ ЗАКАЗА (без сумм!) ===
        card_items = self._make_card(body)
        tk.Label(card_items, text="Состав заказа", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))

        add_frame = tk.Frame(card_items, bg=BG_CARD)
        add_frame.pack(fill="x", pady=(0, 10))

        self.item_combo = ttk.Combobox(add_frame, values=list(TARIFFS.keys()),
                                       state="readonly", font=("Segoe UI", 10), width=26)
        self.item_combo.current(0)
        self.item_combo.pack(side="left", padx=(0, 10))

        tk.Label(add_frame, text="Кол-во:", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 10)).pack(side="left")
        self.qty_entry = tk.Entry(add_frame, font=("Segoe UI", 11), width=5,
                                  bg=FIELD_BG, fg=TEXT_DARK, relief="flat",
                                  highlightthickness=1,
                                  highlightbackground=PINK_MAIN)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(side="left", padx=(4, 8), ipady=4)

        tk.Button(add_frame, text="+ Добавить", command=self._add_item,
                  bg=YELLOW_MAIN, fg=TEXT_DARK, relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground=YELLOW_DARK,
                  padx=12, pady=4).pack(side="left")
        tk.Button(add_frame, text="✕ Удалить", command=self._remove_item,
                  bg=PINK_MAIN, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground=PINK_DARK,
                  padx=12, pady=4).pack(side="left", padx=(6, 0))

        # Таблица позиций (ТОЛЬКО наименование и количество, без цен и сумм)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Pink.Treeview", background=BG_CARD, foreground=TEXT_DARK,
                        fieldbackground=BG_CARD, rowheight=28, font=("Segoe UI", 10))
        style.configure("Pink.Treeview.Heading", background=HEADER_BG,
                        foreground=TEXT_DARK, font=("Segoe UI", 10, "bold"))
        style.map("Pink.Treeview", background=[("selected", "#FFF9C4")])

        cols = ("name", "qty")
        self.tree = ttk.Treeview(card_items, columns=cols, show="headings",
                                 style="Pink.Treeview", height=5)
        self.tree.heading("name", text="Наименование")
        self.tree.heading("qty", text="Кол-во")
        self.tree.column("name", width=300, anchor="w")
        self.tree.column("qty", width=80, anchor="center")
        self.tree.pack(fill="x")

        # === КАРТОЧКА 3: РАСЧЁТ И ДЕЙСТВИЯ ===
        card_footer = self._make_card(body)
        inner_footer = tk.Frame(card_footer, bg=BG_CARD)
        inner_footer.pack(fill="x", padx=16, pady=12)

        # Поле отображения итоговой суммы (заполняется после расчёта)
        sum_frame = tk.Frame(inner_footer, bg=BG_CARD)
        sum_frame.pack(fill="x", pady=(0, 12))
        tk.Label(sum_frame, text="Итого к оплате:", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 12)).pack(side="left")
        self.total_label = tk.Label(sum_frame, text="—", bg=BG_CARD,
                                    fg=TEXT_MUTED, font=("Segoe UI", 14, "bold"))
        self.total_label.pack(side="right")

        # Кнопки действий
        btn_row1 = tk.Frame(inner_footer, bg=BG_CARD)
        btn_row1.pack(fill="x", pady=(0, 8))

        if _CALC_WINDOW_AVAILABLE:
            tk.Button(btn_row1, text="🧮 Открыть калькулятор",
                      command=self._open_calculator_window,
                      bg=YELLOW_MAIN, fg=TEXT_DARK, relief="flat",
                      font=("Segoe UI", 10, "bold"), activebackground=YELLOW_DARK,
                      padx=12, pady=6).pack(side="left", padx=(0, 6))

        tk.Button(btn_row1, text="⚡ Быстрый расчёт",
                  command=self._quick_calc,
                  bg="#81D4FA", fg=TEXT_DARK, relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground="#4FC3F7",
                  padx=12, pady=6).pack(side="left", padx=(0, 6))

        btn_row2 = tk.Frame(inner_footer, bg=BG_CARD)
        btn_row2.pack(fill="x")

        tk.Button(btn_row2, text="🖨 Печать квитанции", command=self._print_receipt,
                  bg=PINK_MAIN, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground=PINK_DARK,
                  padx=12, pady=6).pack(side="left", padx=(0, 6))

        tk.Button(btn_row2, text="🏷 Штрих-коды", command=self._generate_barcodes,
                  bg="#CE93D8", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground="#AB47BC",
                  padx=12, pady=6).pack(side="left", padx=(0, 6))

        tk.Button(btn_row2, text="✓ Оформить заказ", command=self._save_order,
                  bg=TEXT_TOTAL, fg="white", relief="flat",
                  font=("Segoe UI", 11, "bold"), activebackground="#1B5E20",
                  padx=20, pady=6).pack(side="right")

    # ============================= ВСПОМОГАТЕЛЬНЫЕ =============================
    def _make_card(self, parent):
        card = tk.Frame(parent, bg=BG_CARD, highlightbackground=PINK_DARK,
                        highlightthickness=1)
        card.pack(fill="x", pady=(0, 12))
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill="x", padx=18, pady=16)
        return inner

    def _render_cart(self):
        """Перерисовка таблицы позиций (без сумм!)."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for entry in self.cart:
            self.tree.insert("", "end", values=(entry["name"], entry["qty"]))

    # ============================= ЛОГИКА КЛИЕНТА =============================
    def _find_client(self):
        phone = self.client_search.get().strip()
        if phone in MOCK_CLIENTS:
            self.current_client = {"phone": phone, **MOCK_CLIENTS[phone]}
            self.client_info_label.configure(
                text=f"✅ {self.current_client['name']} | Баланс бонусов: {self.current_client['bonus']}",
                fg=TEXT_TOTAL
            )
        else:
            self.current_client = None
            self.client_info_label.configure(
                text="❌ Клиент не найден. Введите +79001234567 для теста.",
                fg="#D32F2F"
            )

    # ============================= ЛОГИКА ПОЗИЦИЙ =============================
    def _add_item(self):
        name = self.item_combo.get()
        if not name:
            messagebox.showwarning("Внимание", "Выберите вещь из списка.")
            return
        try:
            qty = int(self.qty_entry.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Внимание", "Количество должно быть положительным.")
            return

        type_id = TARIFFS[name]["id"]
        # Проверяем, нет ли уже такой позиции — если есть, увеличиваем qty
        for entry in self.cart:
            if entry["type_id"] == type_id:
                entry["qty"] += qty
                self._render_cart()
                return

        self.cart.append({"name": name, "qty": qty, "type_id": type_id})
        self._render_cart()

    def _remove_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите позицию для удаления.")
            return
        idx = self.tree.index(sel[0])
        if 0 <= idx < len(self.cart):
            self.cart.pop(idx)
            self._render_cart()

    # ============================= СВЯЗЬ С CALCULATOR_WINDOW.PY =============================
    def _open_calculator_window(self):
        """
        Открывает CalculatorWindow как модальное окно.
        Передаёт туда текущий cart и client_id, получает обратно итоговую сумму.
        """
        if not self.cart:
            messagebox.showwarning("Внимание", "Сначала добавьте вещи в заказ.")
            return

        if not _CALC_WINDOW_AVAILABLE:
            messagebox.showerror("Ошибка", "calculator_window.py не найден.\n"
                                           "Убедитесь, что файл лежит в той же папке.")
            return

        # Преобразуем cart в список OrderItem для передачи в калькулятор
        items = [OrderItem(entry["type_id"], entry["qty"]) for entry in self.cart]
        client_id = int(self.client_search.get().strip()) if self.current_client else None

        # Создаём CalculatorWindow как модальное окно поверх текущего
        calc_win = CalculatorWindow.__new__(CalculatorWindow)
        # Хак: подменяем __init__ чтобы передать parent и данные
        # Но проще — создать отдельный класс-обёртку или использовать Toplevel.
        # Сделаем через создание нового Tk (отдельное окно) с передачей данных.

        # Вариант: создаём CalculatorWindow и передаём данные через атрибуты
        try:
            # Сохраняем состояние текущего окна
            self.withdraw()

            # Создаём временное окно-контейнер для CalculatorWindow
            temp_root = tk.Tk()
            temp_root.withdraw()  # скрываем root

            # Передаём данные через глобальные переменные модуля (простой способ)
            import calculator_window as cw_mod
            cw_mod._INITIAL_ITEMS = items
            cw_mod._INITIAL_CLIENT_ID = client_id

            # Запускаем CalculatorWindow
            calc_app = CalculatorWindow()
            calc_app.mainloop()

            # Получаем результат (если CalculatorWindow установил его)
            result = getattr(cw_mod, '_CALC_RESULT', None)
            if result is not None:
                self.calculated_total = result.get("total")
                self.total_label.configure(text=f"{self.calculated_total} ₽", fg=TEXT_TOTAL)

            temp_root.destroy()
            self.deiconify()
            self.focus_force()

        except Exception as e:
            self.deiconify()
            messagebox.showerror("Ошибка", f"Не удалось открыть калькулятор:\n{e}")

    def _quick_calc(self):
        """
        Быстрый расчёт через OrderCalculator напрямую (без открытия окна).
        Использует общую бизнес-логику из calculator_module.py.
        """
        if not self.cart:
            messagebox.showwarning("Внимание", "Сначала добавьте вещи в заказ.")
            return

        try:
            items = [OrderItem(entry["type_id"], entry["qty"]) for entry in self.cart]
            client_id = int(self.client_search.get().strip()) if self.current_client else None

            result = self.calculator.calculate_total(items, discount_percent=0,
                                                     client_id=client_id, bonus_to_use=0)
            self.calculated_total = result["total"]
            self.total_label.configure(text=f"{self.calculated_total} ₽", fg=TEXT_TOTAL)

            messagebox.showinfo("Быстрый расчёт",
                                f"Стоимость заказа: {result['total']} ₽\n"
                                f"Позиций: {len(items)}\n\n"
                                f"Для расчёта со скидками и бонусами\n"
                                f"нажмите «Открыть калькулятор».")
        except ValueError as e:
            messagebox.showerror("Ошибка расчёта", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось рассчитать: {e}")

    # ============================= ШТРИХ-КОДЫ И ПЕЧАТЬ =============================
    def _generate_barcodes(self):
        if not self.cart:
            messagebox.showwarning("Внимание", "Сначала добавьте вещи в заказ.")
            return

        self.order_barcodes = [f"BC-{str(uuid.uuid4())[:6].upper()}-{i+1}"
                               for i in range(len(self.cart))]
        bc_text = "\n".join(self.order_barcodes)
        messagebox.showinfo("Штрих-коды сгенерированы",
                            f"Уникальные бирки для заказа:\n\n{bc_text}")

    def _print_receipt(self):
        if not self.cart:
            messagebox.showwarning("Внимание", "Заказ пуст. Нечего печатать.")
            return
        if not self.current_client:
            messagebox.showwarning("Внимание", "Не выбран клиент. Привяжите клиента перед печатью.")
            return
        if self.calculated_total is None:
            messagebox.showwarning("Внимание", "Сначала рассчитайте стоимость заказа.")
            return

        msg = (f"КВИТАНЦИЯ №{str(uuid.uuid4())[:6].upper()}\n"
               f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
               f"Клиент: {self.current_client['name']}\n"
               f"------------------------------\n"
               f"ИТОГО: {self.calculated_total} ₽\n\n"
               f"[Отправлено на принтер]")
        messagebox.showinfo("Печать", msg)

    def _save_order(self):
        if not self.current_client:
            messagebox.showerror("Ошибка", "Необходимо привязать клиента!")
            return
        if not self.cart:
            messagebox.showerror("Ошибка", "Заказ не может быть пустым!")
            return
        if self.calculated_total is None:
            messagebox.showwarning("Внимание", "Сначала рассчитайте стоимость заказа.")
            return

        messagebox.showinfo("Успех",
                            f"Заказ успешно сохранён!\n"
                            f"Клиент: {self.current_client['name']}\n"
                            f"Сумма: {self.calculated_total} ₽\n"
                            f"Позиций: {len(self.cart)}")
        # Очистка формы
        self.cart = []
        self.order_barcodes = []
        self.calculated_total = None
        self._render_cart()
        self.total_label.configure(text="—", fg=TEXT_MUTED)


if __name__ == "__main__":
    OrderWindow().mainloop()