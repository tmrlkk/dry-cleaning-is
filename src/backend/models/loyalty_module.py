from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LoyaltyConfig:
    BONUS_PERCENT = 1
    MAX_BONUS_USAGE_PERCENT = 30
    BONUS_TO_RUBLE = Decimal('1.00')

class ILoyaltyRepository:
    def get_balance(self, client_id: int) -> int:
        raise NotImplementedError
    
    def update_balance(self, client_id: int, new_balance: int) -> bool:
        raise NotImplementedError

class MockLoyaltyRepository(ILoyaltyRepository):
    def __init__(self):
        self._balances = {101: 150, 102: 0, 103: 1000}
    
    def get_balance(self, client_id: int) -> int:
        return self._balances.get(client_id, 0)
    
    def update_balance(self, client_id: int, new_balance: int) -> bool:
        if new_balance < 0:
            return False
        self._balances[client_id] = new_balance
        return True

class LoyaltyService:
    """
    Внешнее описание: Модуль программы лояльности и бонусов.
    Вход: ID клиента, сумма заказа, количество бонусов к списанию.
    Выход: начисленные бонусы, новый баланс, скидка от бонусов.
    """
    def __init__(self, repository: ILoyaltyRepository):
        self.repo = repository
        self.config = LoyaltyConfig()

    def get_balance(self, client_id: int) -> int:
        if client_id <= 0:
            raise ValueError("Некорректный ID клиента")
        return self.repo.get_balance(client_id)

    def calculate_max_bonus_usage(self, order_total: Decimal) -> int:
        if order_total <= 0:
            raise ValueError("Сумма заказа должна быть положительной")
        max_bonus_value = order_total * Decimal(self.config.MAX_BONUS_USAGE_PERCENT) / Decimal('100')
        max_bonus_value = max_bonus_value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        return int(max_bonus_value)

    def apply_bonus_to_order(self, client_id: int, order_total: Decimal, 
                             bonus_to_use: int) -> Tuple[Decimal, int, int]:
        if client_id <= 0:
            raise ValueError("Некорректный ID клиента")
        if order_total <= 0:
            raise ValueError("Сумма заказа должна быть положительной")
        if bonus_to_use < 0:
            raise ValueError("Количество бонусов не может быть отрицательным")
        
        current_balance = self.repo.get_balance(client_id)
        
        # Проверка: бонусов к списанию не больше, чем на балансе
        if bonus_to_use > current_balance:
            raise ValueError(f"Недостаточно бонусов. На балансе: {current_balance}")

            # ИСПРАВЛЕНО: проверка лимита 30% от суммы заказа
        max_allowed = self.calculate_max_bonus_usage(order_total)
        if bonus_to_use > max_allowed:
            raise ValueError(f"Превышен лимит списания бонусов. Максимум: {max_allowed}")
    
        discount_from_bonus = Decimal(bonus_to_use) * self.config.BONUS_TO_RUBLE
        remaining_total = (order_total - discount_from_bonus).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        new_balance = current_balance - bonus_to_use
        if not self.repo.update_balance(client_id, new_balance):
            raise RuntimeError("Ошибка обновления баланса клиента")
        
        logging.info(f"Клиент {client_id}: списано {bonus_to_use} бонусов. "
                    f"Остаток к оплате: {remaining_total} руб. Новый баланс: {new_balance}")
        
        return discount_from_bonus, remaining_total, new_balance

    def accrue_bonus(self, client_id: int, order_total: Decimal) -> Tuple[int, int]:
        if client_id <= 0:
            raise ValueError("Некорректный ID клиента")
        if order_total <= 0:
            raise ValueError("Сумма заказа должна быть положительной")
        
        bonus_earned = int((order_total * Decimal(self.config.BONUS_PERCENT) / Decimal('100')).quantize(
            Decimal('1'), rounding=ROUND_HALF_UP
        ))
        
        current_balance = self.repo.get_balance(client_id)
        new_balance = current_balance + bonus_earned
        
        if not self.repo.update_balance(client_id, new_balance):
            raise RuntimeError("Ошибка обновления баланса клиента")
        
        logging.info(f"Клиент {client_id}: начислено {bonus_earned} бонусов. Новый баланс: {new_balance}")
        
        return bonus_earned, new_balance
    