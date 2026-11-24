import logging

# Настройка логирования для аудита
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MockSmsGateway:
    def send(self, phone: str, message: str) -> str:
        # Имитация успешной отправки
        return f"MSG_ID_{phone[-4:]}"

class NotificationService:
    """
    Внешнее описание: Модуль отправки уведомлений клиентам.
    Вход: номер телефона (str), ID заказа (int)
    Выход: статус отправки (bool), ID сообщения (str)
    Защита: Блок try-except предотвращает падение основного приложения при сбое API.
    """
    def __init__(self, sms_gateway: MockSmsGateway):
        self.sms_gateway = sms_gateway

    def send_order_ready_notification(self, phone: str, order_id: int) -> tuple:
        if not phone or len(phone) < 10:
            logging.warning(f"Некорректный номер телефона для заказа {order_id}")
            return False, None

    def send_notification(self, phone, order_id):
        try:
            message = f"Заказ {order_id} готов"
            msg_id = self.sms_gateway.send(phone, message)
            return True, msg_id
        except ConnectionError as e:
            logging.error(f"Сбой сети при отправке SMS: {e}")
            return False, None
        except Exception as e:
            logging.critical(f"Непредвиденная ошибка: {e}")
            return False, None
        except Exception as e:
            # Защита: изоляция сбоя. Бизнес-процесс выдачи не должен прерываться из-за SMS.
            logging.error(f"Ошибка отправки SMS для заказа {order_id}: {str(e)}")
            return False, None
        