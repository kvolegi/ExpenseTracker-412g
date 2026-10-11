"""
Database connection - Supabase client
"""
from functools import lru_cache
import uuid
from datetime import datetime
from supabase import create_client, Client
from src.core.config import settings
from src.core.logger import logger


class QueryResult:
    def __init__(self, data=None):
        self.data = data or []
        self.error = None


class LocalTableQuery:
    def __init__(self, db, table_name):
        self.db = db
        self.table_name = table_name
        self.filters = []
        self.is_single = False
        self.is_delete = False
        self.update_data = None
        self.insert_data = None
        self.order_field = None
        self.order_desc = False
        self.offset = 0
        self.limit = None

    def insert(self, data):
        self.insert_data = data
        return self

    def select(self, fields="*"):
        return self

    def update(self, data):
        self.update_data = data
        return self

    def delete(self):
        self.is_delete = True
        return self

    def eq(self, field, value):
        self.filters.append((field, value))
        return self

    def or_(self, expr):
        return self

    def gte(self, field, value):
        return self

    def lt(self, field, value):
        return self

    def single(self):
        self.is_single = True
        return self

    def order(self, field, desc=False):
        self.order_field = field
        self.order_desc = desc
        return self

    def range(self, start, end):
        self.offset = start
        self.limit = end - start + 1
        return self

    def execute(self):
        rows = self.db.tables.setdefault(self.table_name, [])

        if self.insert_data is not None:
            items = self.insert_data if isinstance(self.insert_data, list) else [self.insert_data]
            created = []
            for item in items:
                row = dict(item)
                if "id" not in row or not row["id"]:
                    row["id"] = str(uuid.uuid4())
                if "created_at" not in row:
                    row["created_at"] = datetime.now().isoformat()
                rows.append(row)
                created.append(row)
            return QueryResult(created)

        res = list(rows)
        for field, val in self.filters:
            res = [r for r in res if str(r.get(field)) == str(val)]

        if self.table_name == "transactions":
            for tx in res:
                cat_id = tx.get("category_id")
                if cat_id:
                    cat_match = [c for c in self.db.tables.get("categories", []) if str(c.get("id")) == str(cat_id)]
                    tx["category"] = cat_match[0] if cat_match else None
                else:
                    tx["category"] = None

        if self.update_data is not None:
            updated = []
            for r in res:
                r.update(self.update_data)
                updated.append(r)
            return QueryResult(updated)

        if self.is_delete:
            deleted = list(res)
            for r in deleted:
                if r in rows:
                    rows.remove(r)
            return QueryResult(deleted)

        if self.is_single:
            return QueryResult(res[0] if res else None)

        if self.limit:
            res = res[self.offset : self.offset + self.limit]
        elif self.offset:
            res = res[self.offset :]

        return QueryResult(res)


class LocalDatabaseClient:
    def __init__(self):
        self.tables = {
            "categories": [
                {"id": "00000000-0000-0000-0000-000000000001", "name": "Food & Dining", "icon": "🍔", "color": "#FF5722", "type": "expense", "is_default": True},
                {"id": "00000000-0000-0000-0000-000000000002", "name": "Transport", "icon": "🚗", "color": "#2196F3", "type": "expense", "is_default": True},
                {"id": "00000000-0000-0000-0000-000000000003", "name": "Shopping", "icon": "🛍️", "color": "#9C27B0", "type": "expense", "is_default": True},
                {"id": "00000000-0000-0000-0000-000000000004", "name": "Entertainment", "icon": "🎬", "color": "#E91E63", "type": "expense", "is_default": True},
                {"id": "00000000-0000-0000-0000-000000000005", "name": "Health", "icon": "💊", "color": "#4CAF50", "type": "expense", "is_default": True},
                {"id": "00000000-0000-0000-0000-000000000006", "name": "Bills & Utilities", "icon": "📄", "color": "#607D8B", "type": "expense", "is_default": True},
                {"id": "00000000-0000-0000-0000-000000000007", "name": "Salary", "icon": "💵", "color": "#4CAF50", "type": "income", "is_default": True},
                {"id": "00000000-0000-0000-0000-000000000008", "name": "Freelance", "icon": "💻", "color": "#00BCD4", "type": "income", "is_default": True},
                {"id": "00000000-0000-0000-0000-000000000009", "name": "Investment", "icon": "📈", "color": "#FF9800", "type": "income", "is_default": True},
                {"id": "00000000-0000-0000-0000-000000000010", "name": "Gift", "icon": "🎁", "color": "#E91E63", "type": "income", "is_default": True},
            ],
            "users": [],
            "transactions": [],
            "tags": [],
            "expense_tags": [],
            "budgets": [],
            "user_settings": []
        }

    def table(self, name):
        return LocalTableQuery(self, name)


_local_db_singleton = LocalDatabaseClient()


@lru_cache()
def get_supabase() -> Client:
    """Returns singleton Supabase client with local fallback"""
    try:
        if settings.SUPABASE_URL and settings.SUPABASE_KEY and not settings.SUPABASE_KEY.startswith("test"):
            logger.info("Initializing Supabase client", url=settings.SUPABASE_URL[:30] + "...")
            return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    except Exception as e:
        logger.warning("Supabase client init failed, using local offline storage", error=str(e))
    return _local_db_singleton


@lru_cache()
def get_supabase_admin() -> Client:
    """Returns Supabase admin client with local fallback"""
    try:
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY and not settings.SUPABASE_SERVICE_KEY.startswith("test"):
            return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    except Exception as e:
        logger.warning("Supabase admin init failed, using local offline storage", error=str(e))
    return _local_db_singleton

