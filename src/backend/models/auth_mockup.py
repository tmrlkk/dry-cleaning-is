"""
Макет окна входа ИС «ХимчисткаПро» (светлая розово-жёлтая тема).
Без гостевого режима — только вход для работников.
Роли с уровнями доступа:
  - Администратор (полный доступ)
  - Менеджер (приём/выдача заказов, клиенты, отчёты)
  - Кассир (оплата, выдача)
  - Технолог (производственный цикл, контроль качества)
  - Мастер (выполнение чистки, смена статусов)
  - Кладовщик (учёт вещей на складе)
  - Курьер (доставка заказов)
Запуск: python auth_mockup.py
"""
import tkinter as tk
from tkinter import ttk, messagebox

# ============================= ПАЛИТРА =============================
BG_WINDOW    = "#FFF3F6"   # фон окна — очень светлый розовый
BG_CARD      = "#FFFFFF"   # фон карточки с полями — белый
HEADER_BG    = "#FCE4EC"   # шапка окна — нежно-розовый
PINK_MAIN    = "#F48FB1"   # основной розовый
PINK_DARK    = "#EC5F8A"   # розовый для акцентов/рамок
YELLOW_MAIN  = "#FFD54F"   # основной жёлтый
YELLOW_DARK  = "#F5B915"   # жёлтый для акцентов
TEXT_DARK    = "#4A3B3F"   # тёмный текст
TEXT_MUTED   = "#9A8A8F"   # приглушённый текст
TEXT_ACCESS  = "#2E7D32"   # зелёный для уровня доступа
FIELD_BG     = "#FFFFFF"

# ============================= РОЛИ И УРОВНИ ДОСТУПА ================
# Ключ — отображаемое имя, значение — описание прав доступа
ROLES_ACCESS = {
    "Администратор": (
        "Полный доступ: управление пользователями, тарифами, отчётами, "
        "настройками системы, всеми заказами."
    ),
    "Менеджер": (
        "Приём и выдача заказов, работа с клиентами, расчёт стоимости, "
        "печать квитанций, просмотр отчётов."
    ),
    "Кассир": (
        "Приём оплаты, выдача готовых заказов, печать чеков. "
        "Без права редактирования тарифов и удаления заказов."
    ),
    "Технолог": (
        "Управление производственным циклом, назначение заданий мастерам, "
        "контроль качества, смена статусов заказов."
    ),
    "Мастер": (
        "Выполнение работ по заказу (чистка, стирка, глажка), "
        "смена статусов «В работе» → «Готов». Без доступа к финансам."
    ),
    "Кладовщик": (
        "Учёт вещей на складе: приём вещей в хранение, выдача по бирке, "
        "инвентаризация. Без доступа к оплате и клиентам."
    ),
    "Курьер": (
        "Просмотр назначенных доставок, отметка о получении/доставке заказа. "
        "Ограниченный доступ только к своим маршрутам."
    ),
}


class AuthMockupApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ХимчисткаПро — авторизация")
        self.geometry("500x600")
        self.resizable(False, False)
        self.configure(bg=BG_WINDOW)
        self._build_ui()

    # ------------------------- ШАПКА ОКНА -------------------------
    def _build_ui(self):
        # Верхняя полоса с названием и «светофором» из кружков
        header = tk.Frame(self, bg=HEADER_BG, height=34)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="ХимчисткаПро — окно входа",
                 bg=HEADER_BG, fg=TEXT_DARK,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=12)
        dots = tk.Frame(header, bg=HEADER_BG)
        dots.pack(side="right", padx=12)
        for color in ("#FF5F57", "#FEBC2E", "#28C840"):
            cv = tk.Canvas(dots, width=14, height=14, bg=HEADER_BG,
                           highlightthickness=0)
            cv.create_oval(2, 2, 12, 12, fill=color, outline="")
            cv.pack(side="left", padx=3)

        # ------------------------- ТЕЛО -------------------------
        body = tk.Frame(self, bg=BG_WINDOW)
        body.pack(fill="both", expand=True, padx=28, pady=22)

        tk.Label(body, text="Вход в систему", bg=BG_WINDOW, fg=TEXT_DARK,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w")
        tk.Label(body, text="Введите учётные данные сотрудника",
                 bg=BG_WINDOW, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 14))

        # Карточка с полями
        card = tk.Frame(body, bg=BG_CARD, highlightbackground=PINK_DARK,
                        highlightthickness=1)
        card.pack(fill="x", pady=(0, 16))
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill="x", padx=18, pady=16)

        # Логин
        tk.Label(inner, text="Логин", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 10)).pack(anchor="w")
        self.login_box = tk.Entry(inner, font=("Segoe UI", 11),
                                  bg=FIELD_BG, fg=TEXT_DARK,
                                  relief="flat", highlightthickness=1,
                                  highlightbackground=PINK_MAIN,
                                  highlightcolor=YELLOW_DARK)
        self.login_box.pack(fill="x", ipady=5, pady=(2, 12))

        # Пароль
        tk.Label(inner, text="Пароль", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 10)).pack(anchor="w")
        self.pass_box = tk.Entry(inner, font=("Segoe UI", 11), show="•",
                                 bg=FIELD_BG, fg=TEXT_DARK,
                                 relief="flat", highlightthickness=1,
                                 highlightbackground=PINK_MAIN,
                                 highlightcolor=YELLOW_DARK)
        self.pass_box.pack(fill="x", ipady=5, pady=(2, 12))

        # Роль
        tk.Label(inner, text="Роль", bg=BG_CARD, fg=TEXT_DARK,
                 font=("Segoe UI", 10)).pack(anchor="w")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Pink.TCombobox",
                        fieldbackground=FIELD_BG, background=FIELD_BG,
                        foreground=TEXT_DARK, arrowcolor=PINK_DARK,
                        bordercolor=PINK_MAIN, lightcolor=PINK_MAIN,
                        darkcolor=PINK_MAIN)
        self.role_box = ttk.Combobox(
            inner, values=list(ROLES_ACCESS.keys()),
            state="readonly", font=("Segoe UI", 11),
            style="Pink.TCombobox"
        )
        self.role_box.set("Выберите роль…")
        self.role_box.pack(fill="x", ipady=4, pady=(2, 4))
        self.role_box.bind("<<ComboboxSelected>>", self._on_role_changed)

        # Описание уровня доступа (появляется после выбора роли)
        self.access_label = tk.Label(
            inner, text="", bg=BG_CARD, fg=TEXT_ACCESS,
            font=("Segoe UI", 9, "italic"), wraplength=380, justify="left"
        )
        self.access_label.pack(anchor="w", pady=(8, 0))

        # Подсказка
        self.hint = tk.Label(body, text="Режим сотрудника: требуется логин, пароль и роль.",
                             bg=BG_WINDOW, fg=TEXT_MUTED,
                             font=("Segoe UI", 9))
        self.hint.pack(anchor="w", pady=(16, 10))

        # Главная кнопка
        self.btn_action = tk.Button(
            body, text="Войти в систему", command=self._login,
            bg=YELLOW_MAIN, fg=TEXT_DARK, relief="flat",
            font=("Segoe UI", 11, "bold"), activebackground=YELLOW_DARK,
            activeforeground=TEXT_DARK, pady=9
        )
        self.btn_action.pack(fill="x", pady=(4, 12))

        # Вторичная ссылка
        tk.Label(body, text="Забыли пароль?  •  Обратиться к администратору",
                 bg=BG_WINDOW, fg=PINK_DARK, font=("Segoe UI", 9),
                 cursor="hand2").pack()

    # ------------------------- СМЕНА УРОВНЯ ДОСТУПА -------------------------
    def _on_role_changed(self, event=None):
        role = self.role_box.get()
        if role in ROLES_ACCESS:
            self.access_label.configure(
                text=f"Уровень доступа: {ROLES_ACCESS[role]}"
            )
        else:
            self.access_label.configure(text="")

    # --------------------------- ВХОД ---------------------------
    def _login(self):
        login = self.login_box.get().strip()
        password = self.pass_box.get().strip()
        role = self.role_box.get()

        if not login or not password:
            messagebox.showwarning("Внимание", "Заполните логин и пароль.")
            return
        if role == "Выберите роль…":
            messagebox.showwarning("Внимание", "Выберите роль сотрудника.")
            return

        access_desc = ROLES_ACCESS.get(role, "Неизвестный уровень доступа")
        messagebox.showinfo(
            "Вход выполнен",
            f"Здравствуйте, {login}!\n\n"
            f"Роль: {role}\n"
            f"Права доступа:\n{access_desc}"
        )


if __name__ == "__main__":
    AuthMockupApp().mainloop()