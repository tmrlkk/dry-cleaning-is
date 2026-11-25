# Тестовый сценарий для отладки (раздел 11.4)
# Воспроизводит ошибку с неизвестным типом вещи

from calculator_module import OrderCalculator, OrderItem, MockTariffRepository
from notification_module import NotificationService, MockSmsGateway
from loyalty_module import LoyaltyService, MockLoyaltyRepository
from order_module import OrderService

# Инициализация зависимостей
tariff_repo = MockTariffRepository()
calculator = OrderCalculator(tariff_repo)
notifier = NotificationService(MockSmsGateway())
loyalty = LoyaltyService(MockLoyaltyRepository())

order_service = OrderService(calculator, notifier, loyalty)

# Вещь с типом 99 отсутствует в справочнике тарифов
items = [
    OrderItem(item_type_id=1, quantity=2),   # рубашка — есть в тарифах
    OrderItem(item_type_id=99, quantity=1)   # неизвестный тип — НЕТ в тарифах
]

print("=== Создание заказа с неизвестным типом вещи ===")
order = order_service.create_order(
    client_id=101,
    items=items,
    client_phone="+79001234567",
    discount=0,
    bonus_to_use=0
)

if order:
    print(f"✅ Заказ создан. Итоговая сумма: {order['total_cost']} руб.")
else:
    print("❌ Заказ не создан (ошибка)")