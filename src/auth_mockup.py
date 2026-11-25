"""
Макет окна входа ИС «ХимчисткаПро» (светлая розово-жёлтая тема).
Содержит:
  - переключатель режима: «Войти как гость (клиент)» / «Вход для работника»;
  - поля Логин и Пароль;
  - выбор роли: Администратор / Кассир / Менеджер / Технолог / Мастер;
  - имитацию шапки окна с тремя кружками (как на макете-образце).
Запуск: python auth_mockup.py
"""

import tkinter as tk
from tkinter import ttk, messagebox

# ============================ ПАЛИТРА ============================
BG_WINDOW   = "#FFF3F6"   # фон окна — очень светлый розовый
BG_CARD     = "#FFFFFF"   # фон карточки с полями — белый
HEADER_BG   = "#FCE4EC"   # шапка окна — нежно-розовый
PINK_MAIN   = "#F48FB1"   # основной розовый (кнопка гостя)
PINK_DARK   = "#EC5F8A"   # розовый для акцентов/рамок
YELLOW_MAIN = "#FFD54F"   # основной жёлтый (кнопка работника)
YELLOW_DARK = "#F5B915"   # жёлтый для акцентов
TEXT_DARK   = "#4A3B3F"   # тёмный текст
TEXT_MUTED  = "#9A8A8F"   # приглушённый текст
FIELD_BG    = "#FFFFFF"
DISABLED_BG = "#F5F5F5"

ROLES = ["Администратор", "Кассир", "Менеджер", "Технолог", "Мастер"]


class AuthMockupApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ХимчисткаПро — окно входа (макет)")
        self.geometry("460x620")
        self.resizable(False, False)
        self.configure(bg=BG_WINDOW)
        self.mode = "worker"  # текущий режим: guest | worker
        self._build_ui()
        self._apply_mode()

    # ------------------------- ШАПКА ОКНА -------------------------
    def _build_ui(self):
        # Верхняя полоса с названием и «светофором» из кружков
        header = tk.Frame(self, bg=HEADER_BG, height=34)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="ХимчисткаПро — окно входа (макет)",
                 bg=HEADER_BG, fg=TEXT_DARK,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=12)
        dots = tk.Frame(header, bg=HEADER_BG)
        dots.pack(side="right", padx=12)
        for color in ("#FF5F57", "#FEBC2E", "#28C840"):
            tk.Canvas(dots, width=12, height=12, bg=HEADER_BG,
                      highlightthickness=0).pack(side="left", padx=3)
            # рисуем круг
            c = dots.winfo_children()[-1] if False else None
        # перерисуем кружки корректно
        for w in list(dots.winfo_children()):
            w.destroy()
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
        tk.Label(body, text="Выберите, как вы хотите продолжить",
                 bg=BG_WINDOW, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 14))

        # Переключатель режимов (две «вкладки»)
        tabs = tk.Frame(body, bg=BG_WINDOW)
        tabs.pack(fill="x", pady=(0, 16))
        self.btn_guest = tk.Button(
            tabs, text="Я гость (клиент)", command=lambda: self._set_mode("guest"),
            bg=PINK_MAIN, fg="white", relief="flat", font=("Segoe UI", 10, "bold"),
            activebackground=PINK_DARK, activeforeground="white", padx=10, pady=7)
        self.btn_worker = tk.Button(
            tabs, text="Я работник", command=lambda: self._set_mode("worker"),
            bg=YELLOW_MAIN, fg=TEXT_DARK, relief="flat", font=("Segoe UI", 10, "bold"),
            activebackground=YELLOW_DARK, activeforeground=TEXT_DARK, padx=10, pady=7)
        self.btn_guest.pack(side="left", expand=True, fill="x", padx=(0, 6))
        self.btn_worker.pack(side="left", expand=True, fill="x", padx=(6, 0))

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
        self.role_box = ttk.Combobox(inner, values=ROLES, state="readonly",
                                     font=("Segoe UI", 11), style="Pink.TCombobox")
        self.role_box.set("Выберите роль…")
        self.role_box.pack(fill="x", ipady=4, pady=(2, 4))

        # Подсказка
        self.hint = tk.Label(body, text="", bg=BG_WINDOW, fg=TEXT_MUTED,
                             font=("Segoe UI", 9))
        self.hint.pack(anchor="w", pady=(0, 10))

        # Главная кнопка
        self.btn_action = tk.Button(
            body, text="Войти в систему", command=self._login,
            bg=YELLOW_MAIN, fg=TEXT_DARK, relief="flat",
            font=("Segoe UI", 11, "bold"), activebackground=YELLOW_DARK,
            activeforeground=TEXT_DARK, pady=9)
        self.btn_action.pack(fill="x", pady=(4, 12))

        # Вторичная кнопка (ссылка)
        tk.Label(body, text="Забыли пароль?  •  Нет аккаунта? Зарегистрироваться",
                 bg=BG_WINDOW, fg=PINK_DARK, font=("Segoe UI", 9),
                 cursor="hand2").pack()

    # ---------------------- ЛОГИКА РЕЖИМОВ ----------------------
    def _set_mode(self, mode):
        self.mode = mode
        self._apply_mode()

    def _apply_mode(self):
        if self.mode == "guest":
            # Гость: поля недоступны, акцент розовый
            for w in (self.login_box, self.pass_box, self.role_box):
                w.configure(state="disabled")
                try:
                    w.configure(bg=DISABLED_BG, disabledbackground=DISABLED_BG)
                except tk.TclError:
                    pass
            self.role_box.set("—")
            self.btn_guest.configure(bg=PINK_DARK, fg="white")
            self.btn_worker.configure(bg=YELLOW_MAIN, fg=TEXT_DARK)
            self.btn_action.configure(text="Продолжить как гость",
                                      bg=PINK_MAIN, fg="white",
                                      activebackground=PINK_DARK)
            self.hint.configure(text="Гостевой режим: доступ к статусам заказов и тарифам.")
        else:
            # Работник: поля активны, акцент жёлтый
            self.login_box.configure(state="normal", bg=FIELD_BG)
            self.pass_box.configure(state="normal", bg=FIELD_BG)
            self.role_box.configure(state="readonly")
            if self.role_box.get() == "—":
                self.role_box.set("Выберите роль…")
            self.btn_guest.configure(bg=PINK_MAIN, fg="white")
            self.btn_worker.configure(bg=YELLOW_DARK, fg=TEXT_DARK)
            self.btn_action.configure(text="Войти в систему",
                                      bg=YELLOW_MAIN, fg=TEXT_DARK,
                                      activebackground=YELLOW_DARK)
            self.hint.configure(text="Режим сотрудника: требуется логин, пароль и роль.")

    # --------------------------- ВХОД ---------------------------
    def _login(self):
        if self.mode == "guest":
            messagebox.showinfo("Гостевой вход",
                                "Добро пожаловать!\n"
                                "Вы вошли как клиент химчистки.\n"
                                "Доступны: тарифы, статус заказа, программа лояльности.")
            return
        # Работник
        login = self.login_box.get().strip()
        password = self.pass_box.get().strip()
        role = self.role_box.get()
        if not login or not password:
            messagebox.showwarning("Внимание", "Заполните логин и пароль.")
            return
        if role == "Выберите роль…":
            messagebox.showwarning("Внимание", "Выберите роль сотрудника.")
            return
        messagebox.showinfo("Вход выполнен",
                            f"Здравствуйте, {login}!\nРоль: {role}\n"
                            f"Права доступа загружены для роли «{role}».")


if __name__ == "__main__":
    AuthMockupApp().mainloop()