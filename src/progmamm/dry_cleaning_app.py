"""
ИС «Химчистка» — GUI-модуль.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class Service:
    def __init__(self, service_id, name, article, description, price):
        self.service_id = service_id
        self.name = name
        self.article = article
        self.description = description
        self.price = price


class BLService:
    @staticmethod
    def get_all_services():
        return [
            Service(1, "Химчистка пальто", "HC-001", "Верхняя одежда, шерсть/драп. Сушка, глажка.", 500),
            Service(2, "Химчистка костюма мужского", "HC-002", "Костюм-двойка, деликатный режим.", 850),
            Service(3, "Стирка рубашки", "HC-003", "Рубашка, отбеливание, глажка.", 150),
            Service(4, "Пятновыведение", "HC-004", "Локальное удаление пятен любой сложности.", 200),
            Service(5, "Химчистка шубы", "HC-005", "Мех, деликатная химчистка.", 1500),
            Service(6, "Стирка платья", "HC-006", "Платье, ручная стирка.", 350),
            Service(7, "Химчистка брюк", "HC-007", "Брюки, стрелка, глажка.", 300),
            Service(8, "Стирка постельного белья", "HC-008", "Комплект, гипоаллергенное средство.", 400),
        ]


class AuthWindow(tk.Toplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.title("Авторизация")
        self.geometry("320x200")
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.transient(master)
        self.grab_set()
        self.on_success = on_success

        ttk.Label(self, text="Логин:").grid(row=0, column=0, padx=10, pady=(20, 5), sticky="w")
        self.login_box = ttk.Entry(self, width=20)
        self.login_box.grid(row=0, column=1, padx=10, pady=(20, 5))
        self.login_box.insert(0, "admin")

        ttk.Label(self, text="Пароль:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.pass_box = ttk.Entry(self, width=20, show="*")
        self.pass_box.grid(row=1, column=1, padx=10, pady=5)
        self.pass_box.insert(0, "admin")

        ttk.Button(self, text="Войти", command=self._login).grid(row=2, column=1, pady=(15, 0))
        ttk.Button(self, text="Выйти в приложение", command=self._exit).grid(row=3, column=1, pady=5)

    def _login(self):
        login = self.login_box.get().strip().lower()
        password = self.pass_box.get().strip()
        if login == "admin" and password == "admin":
            self.on_success("Администратор")
        elif login == "manager" and password == "manager":
            self.on_success("Менеджер")
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def _exit(self):
        self.destroy()
        self.master.destroy()


class ManagerWindow(tk.Tk):
    def __init__(self, role="Менеджер"):
        super().__init__()
        self.title("Менеджер")
        self.geometry("700x480")
        self.role = role
        self._all_services = []
        self._search_text = ""

        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=8)
        ttk.Label(top, text="Поиск:").pack(side="left")
        self.search_box = ttk.Entry(top, width=30)
        self.search_box.pack(side="left", padx=6)
        self.search_box.bind("<KeyRelease>", self.on_search_text_changed)
        ttk.Button(top, text="Выйти", command=self._logout).pack(side="right")

        self.list_frame = ttk.Frame(self)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        self.canvas = tk.Canvas(self.list_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.status = tk.StringVar(value="Подключено к серверу")
        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x", side="bottom")

        self.load_services()
        self.setup_list_view()

    def load_services(self):
        self._all_services = BLService.get_all_services()

    def setup_list_view(self):
        self._render_list()

    def on_search_text_changed(self, event=None):
        if self.search_box is None:
            return
        self._search_text = self.search_box.get()
        self._render_list()

    def filter_service(self, service):
        if isinstance(service, Service):
            if not self._search_text.strip():
                return True
            search_text = self._search_text.lower()
            return (
                (service.name is not None and search_text in service.name.lower()) or
                (service.article is not None and search_text in service.article.lower()) or
                (service.description is not None and search_text in service.description.lower())
            )
        return False

    def _render_list(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        filtered = [s for s in self._all_services if self.filter_service(s)]
        self.status.set(f"Услуг найдено: {len(filtered)} из {len(self._all_services)}")
        if not filtered:
            ttk.Label(self.scroll_frame, text="Ничего не найдено", foreground="gray").pack(pady=20)
            return
        for s in filtered:
            card = ttk.Frame(self.scroll_frame, relief="groove", borderwidth=1)
            card.pack(fill="x", padx=4, pady=4)
            img = tk.Canvas(card, width=90, height=90, bg="#1a73e8", highlightthickness=0)
            img.pack(side="left", padx=6, pady=6)
            img.create_text(45, 45, text=s.article, fill="white", font=("Segoe UI", 10, "bold"))
            info = ttk.Frame(card)
            info.pack(side="left", fill="both", expand=True, padx=6)
            ttk.Label(info, text=s.name, font=("Segoe UI", 12, "bold")).pack(anchor="w")
            ttk.Label(info, text=f"Артикул: {s.article}", foreground="#555").pack(anchor="w")
            ttk.Label(info, text=s.description, wraplength=480, justify="left").pack(anchor="w")
            ttk.Label(info, text=f"Цена: {s.price} руб.", foreground="#2e7d32",
                      font=("Segoe UI", 11, "bold")).pack(anchor="w")

    def _logout(self):
        self.destroy()
        root = tk.Tk()
        root.withdraw()
        AuthWindow(root, on_success=lambda role: (root.destroy(), AdminWindow() if role == "Администратор" else ManagerWindow(role)))


class AdminWindow(ManagerWindow):
    def __init__(self):
        super().__init__(role="Администратор")
        self.title("Администратор")
        panel = ttk.LabelFrame(self, text="Управление услугами")
        panel.pack(fill="x", padx=10, pady=8)
        ttk.Label(panel, text="Название:").grid(row=0, column=0, padx=4, pady=4, sticky="w")
        self.name_box = ttk.Entry(panel, width=25); self.name_box.grid(row=0, column=1, padx=4)
        ttk.Label(panel, text="Артикул:").grid(row=1, column=0, padx=4, sticky="w")
        self.art_box = ttk.Entry(panel, width=25); self.art_box.grid(row=1, column=1, padx=4)
        ttk.Label(panel, text="Описание:").grid(row=2, column=0, padx=4, sticky="w")
        self.desc_box = ttk.Entry(panel, width=25); self.desc_box.grid(row=2, column=1, padx=4)
        ttk.Label(panel, text="Цена:").grid(row=3, column=0, padx=4, sticky="w")
        self.price_box = ttk.Entry(panel, width=25); self.price_box.grid(row=3, column=1, padx=4)
        ttk.Button(panel, text="Добавить услугу", command=self._add_service).grid(row=4, column=1, pady=6, sticky="e")

    def _add_service(self):
        name = self.name_box.get().strip()
        article = self.art_box.get().strip()
        if not name or not article:
            messagebox.showwarning("Внимание", "Заполните название и артикул")
            return
        try:
            price = int(self.price_box.get() or 0)
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом")
            return
        self._all_services.append(Service(len(self._all_services) + 1, name, article,
                                          self.desc_box.get().strip(), price))
        self._render_list()
        for box in (self.name_box, self.art_box, self.desc_box, self.price_box):
            box.delete(0, tk.END)


def main():
    root = tk.Tk()
    root.withdraw()
    def on_success(role):
        root.destroy()
        if role == "Администратор":
            AdminWindow().mainloop()
        else:
            ManagerWindow(role).mainloop()
    AuthWindow(root, on_success)
    root.mainloop()


if __name__ == "__main__":
    main()