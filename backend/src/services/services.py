"""
Services - Application Business Logic Layer (Лабораторна робота №2)
Багатошарова архітектура: шар застосунку координує виконання сценаріїв
та взаємодіє з репозиторіями для збереження даних.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from src.core.logger import logger
from src.core.security import hash_password, verify_password, create_access_token
from src.models.schemas import TransactionCreate, TransactionUpdate
from src.repositories.repositories import (
    TransactionRepository, CategoryRepository, UserRepository
)
from src.validators.expense_validator import ExpenseValidator


# ============================================
# AUTH SERVICE (Сценарій: Автентифікація)
# ============================================
class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    async def register(self, email: str, password: str, username: Optional[str] = None) -> dict:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        user_data = {
            "email": email,
            "password_hash": hash_password(password),
            "username": username,
        }
        user = await self.user_repo.create(user_data)
        token = create_access_token({"sub": user["id"], "email": email})
        logger.info("User registered", user_id=user["id"])
        return {"access_token": token, "token_type": "bearer", "user": user}

    async def login(self, email: str, password: str) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.get("password_hash", "")):
            raise ValueError("Invalid credentials")
        token = create_access_token({"sub": user["id"], "email": email})
        logger.info("User logged in", user_id=user["id"])
        return {"access_token": token, "token_type": "bearer", "user": user}

    async def telegram_login(self, telegram_data: dict) -> dict:
        logger.info("telegram_login start", tg_id=telegram_data.get("id"))
        try:
            user = await self.user_repo.upsert_telegram_user(telegram_data)
            logger.info("upsert_telegram_user success", user_id=user.get("id") if user else None)
        except Exception as e:
            logger.error("upsert_telegram_user failed", error=str(e), type=type(e).__name__)
            raise
        
        try:
            token = create_access_token({"sub": user["id"], "telegram_id": telegram_data["id"]})
            logger.info("Token created", user_id=user.get("id"))
        except Exception as e:
            logger.error("Token creation failed", error=str(e), type=type(e).__name__)
            raise
        
        logger.info("Telegram login success", user_id=user.get("id"), tg=telegram_data.get("id"))
        return {"access_token": token, "token_type": "bearer", "user": user}


# ============================================
# TRANSACTION SERVICE (Сценарій: Облік транзакцій)
# ============================================
class TransactionService:
    def __init__(self):
        self.tx_repo = TransactionRepository()

    async def create_transaction(self, user_id: str, data: TransactionCreate) -> dict:
        ExpenseValidator.validate(data.model_dump())

        expense_data = {
            "type": data.type,
            "amount": float(data.amount),
            "currency": data.currency,
            "category_id": str(data.category_id) if data.category_id else None,
            "comment": data.comment,
            "payment_method": data.payment_method,
            "transaction_date": data.transaction_date.isoformat() if data.transaction_date else None,
            "tag_ids": [str(tid) for tid in (data.tag_ids or [])]
        }

        transaction = await self.tx_repo.create(user_id, expense_data)
        logger.info("Transaction recorded", id=transaction.get("id"), user_id=user_id)
        return transaction

    async def get_transactions(
        self,
        user_id: str,
        type_filter: Optional[str] = None,
        category_id: Optional[str] = None,
        month: Optional[str] = None,
        sort_by: str = "date",
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        items = await self.tx_repo.get_all(
            user_id, type_filter, category_id, month, limit, offset
        )

        if sort_by == "amount":
            items = sorted(items, key=lambda x: float(x.get("amount", 0)), reverse=True)
        elif sort_by == "category":
            items = sorted(
                items,
                key=lambda x: (x.get("category") or {}).get("name", "") if isinstance(x.get("category"), dict) else ""
            )
        else:
            items = sorted(items, key=lambda x: str(x.get("transaction_date", "")), reverse=True)

        income_total = sum(float(t.get("amount", 0)) for t in items if t.get("type") == "income")
        expense_total = sum(float(t.get("amount", 0)) for t in items if t.get("type") == "expense")

        return {
            "items": items,
            "total": len(items),
            "income_total": income_total,
            "expense_total": expense_total,
            "balance": income_total - expense_total,
        }

    async def update_transaction(self, tx_id: str, user_id: str, data: TransactionUpdate) -> Optional[dict]:
        update_data = data.model_dump(exclude_unset=True)
        return await self.tx_repo.update(tx_id, user_id, update_data)

    async def delete_transaction(self, tx_id: str, user_id: str) -> bool:
        return await self.tx_repo.delete(tx_id, user_id)

    async def get_stats(self, user_id: str, month: Optional[str] = None) -> dict:
        return await self.tx_repo.get_stats(user_id, month)


TransactionFacade = TransactionService


# ============================================
# CATEGORY SERVICE
# ============================================
class CategoryService:
    def __init__(self):
        self.cat_repo = CategoryRepository()

    async def get_all(self, user_id: str) -> list:
        return await self.cat_repo.get_all(user_id)

    async def create(self, user_id: str, data: dict) -> dict:
        return await self.cat_repo.create(user_id, data)

    async def update(self, cat_id: str, user_id: str, data: dict) -> Optional[dict]:
        return await self.cat_repo.update(cat_id, user_id, data)

    async def delete(self, cat_id: str, user_id: str) -> bool:
        return await self.cat_repo.delete(cat_id, user_id)
