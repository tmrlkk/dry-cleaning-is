"""
Окно расчёта стоимости ИС «ХимчисткаПро» (светлая розово-жёлтая тема).
Функционал:
- Состав заказа из тарифов (вещи + количество)
- Дополнительные услуги (фиксированные надбавки как позиции)
- Скидка по дисконтной карте (процент)
- Списание бонусов программы лояльности (если подключён loyalty_module)
- Итоговый расчёт через OrderCalculator.calculate_total()
Запуск: python calculator_window.py
(требуется calculator_module.py в той же папке)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal

# --- Интеграция с реальным модулем расчёта ---
from calculator_module import OrderCalculator, OrderItem

# --- Опциональная интеграция с программой лояльности (M6) ---
try:
    from loyalty_module import LoyaltyService, MockLoyaltyRepository
    _LOYALTY_AVAILABLE = True
except ImportError:
    LoyaltyService = None
    MockLoyaltyRepository = None
    _LOYALTY_AVAILABLE = False

# ============================= ПАЛИТРА (как в auth_mockup.py) =============================
BG_WINDOW    = "#FFF3F6"   # фон окна — очень светлый розовый
BG_CARD      = "#FFFFFF"   # фон карточки — белый
HEADER_BG    = "#FCE4EC"   # шапка окна — нежно-розовый
PINK_MAIN    = "#F48FB1"   # основной розовый
PINK_DARK    = "#EC5F8A"   # розовый для акцентов/рамок
YELLOW_MAIN  = "#FFD54F"   # основной жёлтый
YELLOW_DARK  = "#F5B915"   # жёлтый для акцентов
TEXT_DARK    = "#4A3B3F"   # тёмный текст
TEXT_MUTED   = "#9A8A8F"   # приглушённый текст
TEXT_TOTAL   = "#2E7D32"   # зелёный для итоговой суммы
FIELD_BG     = "#FFFFFF"

# ============================= РАСШИРЕННЫЙ СПРАВОЧНИК ТАРИФОВ =============================
# id 1-3 — базовые вещи (совпадают с MockTariffRepository), id 10+ — доп. услуги
TARIFFS = {
    1:  ("Рубашка", Decimal("150.00")),
    2:  ("Брюки", Decimal("300.00")),
    3:  ("Пальто", Decimal("500.00")),
    4:  ("Костюм-двойка", Decimal("850.00")),
    10: ("Пятновыведение", Decimal("150.00")),
    11: ("Антибактериальная обработка", Decimal("100.00")),
    12: ("Срочность (+1 день)", Decimal("200.00")),
    13: ("Деликатная стирка", Decimal("120.00")),
}

# Доп. услуги, которые добавляются чекбоксами (id -> название)
EXTRA_SERVICES = {10: "Пятновыведение", 11: "Антибактериальная",
                  12: "Срочность", 13: "Деликатная стирка"}


class ExtendedTariffRepository:
    """Реализует интерфейс get_price() для OrderCalculator,
    покрывая и вещи, и доп. услуги."""
    def get_price(self, item_type_id: int) -> Decimal:
        if item_type_id in TARIFFS:
            return TARIFFS[item_type_id][1]
        return Decimal("0.00")


class CalculatorWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ХимчисткаПро — расчёт стоимости")
        self.geometry("780x760")
        self.resizable(False, False)
        self.configure(bg=BG_WINDOW)

        # Бизнес-зависимости (DI, как в OrderService)
        self.tariff_repo = ExtendedTariffRepository()
        self.loyalty_service = (
            LoyaltyService(MockLoyaltyRepository()) if _LOYALTY_AVAILABLE else None
        )
        self.calculator = OrderCalculator(self.tariff_repo, self.loyalty_service)

        # Состояние
        self.cart = []          # список OrderItem
        self.extra_vars = {}    # чекбоксы доп. услуг -> BooleanVar

        self._build_ui()
        self._recalculate()

    # ------------------------- ШАПКА ОКНА -------------------------
    def _build_ui(self):
        header = tk.Frame(self, bg=HEADER_BG, height=34)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="ХимчисткаПро — расчёт стоимости",
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
        body.pack(fill="both", expand=True, padx=24, pady=18)

        tk.Label(body, text="Расчёт стоимости заказа", bg=BG_WINDOW, fg=TEXT_DARK,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w")
        tk.Label(body, text="Состав заказа, доп. услуги, скидки и бонусы",
                 bg=BG_WINDOW, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 12))

        self._card_client(body)
        self._card_items(body)
        self._card_extras(body)
        self._card_discount(body)
        self._card_total(body)
        self._card_actions(body)

    # ---------------- КАРТОЧКА: КЛИЕНТ ----------------
    def _card_client(self, parent):
        card = self._make_card(parent)
        tk.Label(card, text="Клиент", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        row = tk.Frame(card, bg=BG_CARD)
        row.pack(fill="x")
        tk.Label(row, text="ID клиента:", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 10)).pack(side="left")
        self.client_id_box = tk.Entry(row, font=("Segoe UI", 11), width=8,
                                      bg=FIELD_BG, fg=TEXT_DARK, relief="flat",
                                      highlightthickness=1,
                                      highlightbackground=PINK_MAIN,
                                      highlightcolor=YELLOW_DARK)
        self.client_id_box.insert(0, "101")
        self.client_id_box.pack(side="left", padx=(6, 16), ipady=4)
        hint = ("Бонусы активны (M6 подключён)" if _LOYALTY_AVAILABLE
                else "Бонусы недоступны: loyalty_module не найден")
        tk.Label(row, text=hint, bg=BG_CARD,
                 fg=TEXT_TOTAL if _LOYALTY_AVAILABLE else TEXT_MUTED,
                 font=("Segoe UI", 9, "italic")).pack(side="left")

    # ---------------- КАРТОЧКА: СОСТАВ ЗАКАЗА ----------------
    def _card_items(self, parent):
        card = self._make_card(parent)
        tk.Label(card, text="Состав заказа", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))

        add_row = tk.Frame(card, bg=BG_CARD)
        add_row.pack(fill="x", pady=(0, 8))
        self.item_combo = ttk.Combobox(
            add_row, values=[f"{name} ({price} ₽)" for _, (name, price) in TARIFFS.items() if _ < 10],
            state="readonly", font=("Segoe UI", 10), width=26)
        self.item_combo.current(0)
        self.item_combo.pack(side="left", padx=(0, 8))

        tk.Label(add_row, text="Кол-во:", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 10)).pack(side="left")
        self.qty_box = tk.Entry(add_row, font=("Segoe UI", 11), width=5,
                                 bg=FIELD_BG, fg=TEXT_DARK, relief="flat",
                                 highlightthickness=1,
                                 highlightbackground=PINK_MAIN)
        self.qty_box.insert(0, "1")
        self.qty_box.pack(side="left", padx=(4, 8), ipady=4)

        tk.Button(add_row, text="+ Добавить", command=self._add_item,
                  bg=YELLOW_MAIN, fg=TEXT_DARK, relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground=YELLOW_DARK,
                  padx=12, pady=4).pack(side="left")
        tk.Button(add_row, text="✕ Удалить", command=self._remove_item,
                  bg=PINK_MAIN, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground=PINK_DARK,
                  padx=12, pady=4).pack(side="left", padx=(6, 0))

        # Таблица позиций
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Pink.Treeview", background=BG_CARD, foreground=TEXT_DARK,
                        fieldbackground=BG_CARD, rowheight=26, font=("Segoe UI", 10))
        style.configure("Pink.Treeview.Heading", background=HEADER_BG,
                        foreground=TEXT_DARK, font=("Segoe UI", 10, "bold"))
        style.map("Pink.Treeview", background=[("selected", "#FFF9C4")])

        cols = ("name", "qty", "price", "sum")
        self.tree = ttk.Treeview(card, columns=cols, show="headings",
                                 style="Pink.Treeview", height=5)
        for c, t, w, a in [("name", "Наименование", 220, "w"),
                           ("qty", "Кол-во", 60, "center"),
                           ("price", "Цена", 80, "e"),
                           ("sum", "Сумма", 90, "e")]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor=a)
        self.tree.pack(fill="x")

    # ---------------- КАРТОЧКА: ДОП. УСЛУГИ ----------------
    def _card_extras(self, parent):
        card = self._make_card(parent)
        tk.Label(card, text="Дополнительные услуги", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        grid = tk.Frame(card, bg=BG_CARD)
        grid.pack(fill="x")
        for i, (sid, name) in enumerate(EXTRA_SERVICES.items()):
            var = tk.BooleanVar(value=False)
            self.extra_vars[sid] = var
            price = TARIFFS[sid][1]
            cb = tk.Checkbutton(grid, text=f"{name} (+{price} ₽)", variable=var,
                                 bg=BG_CARD, fg=TEXT_DARK,
                                 font=("Segoe UI", 10),
                                 selectcolor=FIELD_BG,
                                 activebackground=BG_CARD,
                                 command=self._toggle_extra)
            cb.grid(row=i // 2, column=i % 2, sticky="w", padx=8, pady=4)

    # ---------------- КАРТОЧКА: СКИДКИ ----------------
    def _card_discount(self, parent):
        card = self._make_card(parent)
        tk.Label(card, text="Скидки и бонусы", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        row = tk.Frame(card, bg=BG_CARD)
        row.pack(fill="x")
        tk.Label(row, text="Скидка по карте (%):", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 10)).pack(side="left")
        self.discount_box = tk.Entry(row, font=("Segoe UI", 11), width=6,
                                     bg=FIELD_BG, fg=TEXT_DARK, relief="flat",
                                     highlightthickness=1,
                                     highlightbackground=PINK_MAIN,
                                     highlightcolor=YELLOW_DARK)
        self.discount_box.insert(0, "0")
        self.discount_box.pack(side="left", padx=(6, 20), ipady=4)
        self.discount_box.bind("<KeyRelease>", lambda e: self._recalculate())

        tk.Label(row, text="Бонусы к списанию:", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 10)).pack(side="left")
        self.bonus_box = tk.Entry(row, font=("Segoe UI", 11), width=6,
                                  bg=FIELD_BG, fg=TEXT_DARK, relief="flat",
                                  highlightthickness=1,
                                  highlightbackground=PINK_MAIN,
                                  highlightcolor=YELLOW_DARK)
        self.bonus_box.insert(0, "0")
        self.bonus_box.pack(side="left", padx=(6, 0), ipady=4)
        self.bonus_box.bind("<KeyRelease>", lambda e: self._recalculate())

    # ---------------- КАРТОЧКА: ИТОГ ----------------
    def _card_total(self, parent):
        card = self._make_card(parent)
        tk.Label(card, text="Итог расчёта", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        self.lbl_subtotal = self._result_row(card, "Стоимость (subtotal)")
        self.lbl_discount = self._result_row(card, "Скидка по карте")
        self.lbl_bonus = self._result_row(card, "Списание бонусов")
        self.lbl_total = self._result_row(card, "ИТОГО К ОПЛАТЕ", bold=True,
                                          color=TEXT_TOTAL)

    # ---------------- КАРТОЧКА: ДЕЙСТВИЯ ----------------
    def _card_actions(self, parent):
        row = tk.Frame(parent, bg=BG_WINDOW)
        row.pack(fill="x", pady=(14, 0))
        tk.Button(row, text="⟳ Пересчитать", command=self._recalculate,
                  bg=YELLOW_MAIN, fg=TEXT_DARK, relief="flat",
                  font=("Segoe UI", 11, "bold"), activebackground=YELLOW_DARK,
                  padx=16, pady=7).pack(side="left", padx=(0, 8))
        tk.Button(row, text="Очистить", command=self._clear,
                  bg=PINK_MAIN, fg="white", relief="flat",
                  font=("Segoe UI", 11, "bold"), activebackground=PINK_DARK,
                  padx=16, pady=7).pack(side="left", padx=(0, 8))
        tk.Button(row, text="✓ Оформить заказ", command=self._save_order,
                  bg=TEXT_TOTAL, fg="white", relief="flat",
                  font=("Segoe UI", 11, "bold"), activebackground="#1B5E20",
                  padx=16, pady=7).pack(side="right")

    # ============================= ВСПОМОГАТЕЛЬНОЕ =============================
    def _make_card(self, parent):
        card = tk.Frame(parent, bg=BG_CARD, highlightbackground=PINK_DARK,
                        highlightthickness=1)
        card.pack(fill="x", pady=(0, 12))
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill="x", padx=16, pady=12)
        return inner

    def _result_row(self, parent, label, bold=False, color=TEXT_DARK):
        row = tk.Frame(parent, bg=BG_CARD)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, bg=BG_CARD, fg=TEXT_MUTED,
                 font=("Segoe UI", 10, "bold" if bold else "normal")).pack(side="left")
        val = tk.Label(row, text="—", bg=BG_CARD, fg=color,
                       font=("Segoe UI", 11, "bold"))
        val.pack(side="right")
        return val

    # ============================= ЛОГИКА =============================
    def _combo_id(self):
        """Извлекает item_type_id из выбранной строки комбобокса."""
        text = self.item_combo.get()
        for tid, (name, _) in TARIFFS.items():
            if text.startswith(f"{name} ("):
                return tid
        return None

    def _add_item(self):
        tid = self._combo_id()
        if tid is None:
            messagebox.showwarning("Внимание", "Выберите позицию.")
            return
        try:
            qty = int(self.qty_box.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Внимание", "Количество должно быть положительным.")
            return
        self.cart.append(OrderItem(item_type_id=tid, quantity=qty))
        self._render_cart()
        self._recalculate()

    def _remove_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите позицию для удаления.")
            return
        idx = self.tree.index(sel[0])
        # позиции доп. услуг удаляются чекбоксами, из cart удаляем только базовые
        if 0 <= idx < len(self.cart):
            self.cart.pop(idx)
            self._render_cart()
            self._recalculate()

    def _toggle_extra(self):
        """Синхронизирует чекбоксы доп. услуг с cart (по одной позиции qty=1)."""
        for sid, var in self.extra_vars.items():
            present = any(i.item_type_id == sid for i in self.cart)
            if var.get() and not present:
                self.cart.append(OrderItem(item_type_id=sid, quantity=1))
            elif not var.get() and present:
                self.cart = [i for i in self.cart if i.item_type_id != sid]
        self._render_cart()
        self._recalculate()

    def _render_cart(self):
        for it in self.tree.get_children():
            self.tree.delete(it)
        for item in self.cart:
            name, price = TARIFFS[item.item_type_id]
            total = price * item.quantity
            self.tree.insert("", "end",
                             values=(name, item.quantity, f"{price} ₽", f"{total} ₽"))

    def _recalculate(self):
        try:
            discount = int(self.discount_box.get() or 0)
            bonus = int(self.bonus_box.get() or 0)
        except ValueError:
            self._show_error("Скидка и бонусы должны быть целыми числами.")
            return
        if not self.cart:
            self._set_results(Decimal("0.00"), Decimal("0.00"),
                              Decimal("0.00"), Decimal("0.00"))
            return
        try:
            cid = int(self.client_id_box.get()) if self.client_id_box.get().strip() else None
        except ValueError:
            cid = None
        try:
            res = self.calculator.calculate_total(
                self.cart, discount, client_id=cid, bonus_to_use=bonus)
            self._set_results(res["subtotal"], res["discount_amount"],
                              res["bonus_discount"], res["total"])
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(f"Ошибка расчёта: {e}")

    def _set_results(self, subtotal, discount, bonus, total):
        self.lbl_subtotal.configure(text=f"{subtotal} ₽")
        self.lbl_discount.configure(text=f"−{discount} ₽")
        self.lbl_bonus.configure(text=f"−{bonus} ₽")
        self.lbl_total.configure(text=f"{total} ₽")

    def _show_error(self, msg):
        self.lbl_subtotal.configure(text="—")
        self.lbl_discount.configure(text="—")
        self.lbl_bonus.configure(text="—")
        self.lbl_total.configure(text="ошибка", fg="#D32F2F")
        messagebox.showerror("Ошибка расчёта", msg)

    def _clear(self):
        self.cart = []
        for var in self.extra_vars.values():
            var.set(False)
        self.discount_box.delete(0, tk.END); self.discount_box.insert(0, "0")
        self.bonus_box.delete(0, tk.END); self.bonus_box.insert(0, "0")
        self._render_cart()
        self._recalculate()

    def _save_order(self):
        if not self.cart:
            messagebox.showwarning("Внимание", "Заказ пуст — добавьте позиции.")
            return
        total = self.lbl_total["text"]
        # В реальном проекте здесь вызывается OrderService.create_order(...)
        messagebox.showinfo(
            "Расчёт сохранён",
            f"Итоговая сумма: {total}\n\n"
            "Данные переданы в модуль оформления заказа (M3)."
        )


if __name__ == "__main__":
    CalculatorWindow().mainloop()