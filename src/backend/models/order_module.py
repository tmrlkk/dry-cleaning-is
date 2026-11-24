import uuid

class OrderService:
    """
    Внешнее описание: Модуль оформления и сохранения заказа.
    Вход: ID клиента, список вещей, номер телефона для уведомления.
    Выход: объект созданного заказа (dict).
    Защита: Генерация уникального UUID для заказа, транзакционный подход (все или ничего).
    """
    def __init__(self, calculator: OrderCalculator, notifier: NotificationService):
        self.calculator = calculator
        self.notifier = notifier
        self._db_orders = {} # Имитация БД заказов

    def create_order(self, client_id: int, items: list, client_phone: str, discount: int = 0) -> dict:
        try:
            # 1. Расчет стоимости (используем модуль M4)
            cost_breakdown = self.calculator.calculate_total(items, discount)
            
            # 2. Генерация уникального ID заказа и штрих-кодов
            order_id = str(uuid.uuid4())[:8].upper()
            barcodes = [f"BC-{order_id}-{i}" for i in range(len(items))]
            
            # 3. Формирование объекта заказа (имитация сохранения в БД)
            order = {
                "order_id": order_id,
                "client_id": client_id,
                "items": [{"type": i.item_type_id, "qty": i.quantity} for i in items],
                "total_cost": cost_breakdown["total"],
                "status": "Создан",
                "barcodes": barcodes
            }
            self._db_orders[order_id] = order
            
            # 4. Имитация печати квитанции
            print(f"[ПРИНТЕР] Печать квитанции для заказа {order_id} на сумму {cost_breakdown['total']} руб.")
            
            return order
            
        except ValueError as ve:
            print(f"[ОШИБКА ВАЛИДАЦИИ] Не удалось создать заказ: {ve}")
            return None
        except Exception as e:
            print(f"[КРИТИЧЕСКАЯ ОШИБКА] Сбой при создании заказа: {e}")
            return None

    def complete_order(self, order_id: str, client_phone: str):
        if order_id in self._db_orders:
            self._db_orders[order_id]["status"] = "Готов к выдаче"
            # Вызов модуля M5
            self.notifier.send_order_ready_notification(client_phone, order_id)
            print(f"[СИСТЕМА] Заказ {order_id} завершен и выдан.")
            