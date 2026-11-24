import hashlib
import datetime
from typing import Optional, Dict, Tuple

class AuthResult:
    SUCCESS = "Success"
    INVALID_CREDENTIALS = "InvalidCredentials"
    ACCOUNT_LOCKED = "AccountLocked"

class UserSession:
    def __init__(self, user_id: int, full_name: str, role: str):
        self.user_id = user_id
        self.full_name = full_name
        self.role = role
        self.login_time = datetime.datetime.now()

class MockUserRepository:
    """Заглушка репозитория пользователей (имитация БД)"""
    def __init__(self):
        # Храним: login: {id, name, role, password_hash, salt, failed_attempts}
        self.users = {
            "admin": {
                "id": 1, "name": "Иванов И.И.", "role": "Администратор",
                "salt": "s3cr3t_s4lt", "failed_attempts": 0,
                "password_hash": hashlib.sha256(("admin123" + "s3cr3t_s4lt").encode()).hexdigest()
            }
        }

    def get_user(self, login: str) -> Optional[dict]:
        return self.users.get(login)

    def increment_failed_attempts(self, login: str):
        if login in self.users:
            self.users[login]["failed_attempts"] += 1

    def reset_failed_attempts(self, login: str):
        if login in self.users:
            self.users[login]["failed_attempts"] = 0

class AuthService:
    """
    Внешнее описание: Модуль аутентификации пользователей.
    Вход: login (str), password (str)
    Выход: кортеж (статус AuthResult, объект UserSession или None)
    Защита: Хеширование SHA-256 с солью, блокировка после 5 неудачных попыток.
    """
    MAX_FAILED_ATTEMPTS = 5

    def __init__(self, repository: MockUserRepository):
        self.repo = repository

    def authenticate(self, login: str, password: str) -> Tuple[str, Optional[UserSession]]:
        user = self.repo.get_user(login)
        
        # Защита: проверка на блокировку
        if user and user["failed_attempts"] >= self.MAX_FAILED_ATTEMPTS:
            return AuthResult.ACCOUNT_LOCKED, None
            
        if not user:
            return AuthResult.INVALID_CREDENTIALS, None

        # Защита: проверка хеша пароля
        password_hash = hashlib.sha256((password + user["salt"]).encode()).hexdigest()
        
        if user["password_hash"] != password_hash:
            self.repo.increment_failed_attempts(login)
            return AuthResult.INVALID_CREDENTIALS, None

        # Успешный вход
        self.repo.reset_failed_attempts(login)
        session = UserSession(user["id"], user["name"], user["role"])
        return AuthResult.SUCCESS, session