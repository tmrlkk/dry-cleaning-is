from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional
from loyalty_module import LoyaltyService

class OrderItem:
    def __init__(self, item_type_id: int, quantity: int):
        self.item_type_id = item_type_id
        self.quantity = quantity

class MockTariffRepository:
    """Заглушка справочника тарифов"""
    def get_price(self, item_type_id: int) -> Decimal:
        tariffs = {1: Decimal('150.00'), 2: Decimal('300.00'), 3: Decimal('500.00')} # 1-рубашка, 2-брюки, 3-пальто
        return tariffs.get(item_type_id, Decimal('0.00'))

class OrderCalculator:
    """
    Внешнее описание: Модуль расчета стоимости заказа.
    Вход: список OrderItem, процент скидки (int)
    Выход: словарь с детализацией (subtotal, discount, total)
    Защита: Валидация входных данных, использование Decimal для исключения ошибок округления float.
    """
    def __init__(self, tariff_repo: MockTariffRepository,
                 loyalty_service: Optional[LoyaltyService] = None):
        self.tariff_repo = tariff_repo
        self.loyalty_service = loyalty_service  # M6 — необязательная зависимость

    def calculate_total(self, items: List[OrderItem], discount_percent: int,
                        client_id: int = None, bonus_to_use: int = 0) -> Dict[str, Decimal]:
        # Защита: валидация входных данных
        if not items:
            raise ValueError("Список вещей не может быть пустым")
        if not (0 <= discount_percent <= 100):
            raise ValueError("Скидка должна быть в диапазоне от 0 до 100")

        subtotal = Decimal('0.00')
        details = {}

        for item in items:
            if item.quantity <= 0:
                raise ValueError("Количество вещей должно быть положительным")
            
            price = self.tariff_repo.get_price(item.item_type_id)
            item_total = price * item.quantity
            subtotal += item_total
            details[f"Тип_{item.item_type_id}"] = item_total

        # Расчет скидки с правильным округлением до копеек
        discount_amount = (subtotal * Decimal(discount_percent) / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_after_discount = subtotal - discount_amount
        # НОВОЕ: списание бонусов через модуль M6
        bonus_discount = Decimal('0.00')
        if client_id and self.loyalty_service and bonus_to_use > 0:
            bonus_discount, _, _ = self.loyalty_service.apply_bonus_to_order(
                client_id, total_after_discount, bonus_to_use
            )
        total = (total_after_discount - bonus_discount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return {
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "bonus_discount": bonus_discount,
            "total": total,
            "details": details
        }
    