# 🗄️ Архітектура даних та сховища (Лабораторна робота №5)

## 1. Загальний огляд
Дані системи **Expense Tracker** зберігаються у хмарній реляційній системі керування базами даних **PostgreSQL 16** під управлінням платформи **Supabase**. Архітектура орієнтована на забезпечення суворої ізоляції користувачів, високої швидкодії аналітичних вибірок та дотримання цілісності фінансових операцій.

---

## 2. Реляційна модель та 3NF-нормалізація

Схема складається з 7 основних таблиць, спроєктованих у **третій нормальній формі (3NF)**:

```mermaid
erDiagram
    USERS ||--o{ TRANSACTIONS : "has"
    USERS ||--o{ CATEGORIES : "creates"
    USERS ||--o{ BUDGETS : "sets"
    USERS ||--o{ USER_SETTINGS : "configures"
    USERS ||--o{ TAGS : "creates"
    CATEGORIES ||--o{ TRANSACTIONS : "classifies"
    TRANSACTIONS ||--o{ EXPENSE_TAGS : "tagged with"
    TAGS ||--o{ EXPENSE_TAGS : "belongs to"

    USERS {
        uuid id PK
        int8 telegram_id UK
        string email UK
        string password_hash
        string username
        string first_name
        string last_name
        string avatar_url
        timestamptz created_at
        timestamptz updated_at
    }

    CATEGORIES {
        uuid id PK
        uuid user_id FK
        string name
        string icon
        string color
        string type
        bool is_default
        timestamptz created_at
    }

    TRANSACTIONS {
        uuid id PK
        uuid user_id FK
        uuid category_id FK
        decimal amount
        string currency
        string type
        string comment
        string payment_method
        timestamptz transaction_date
        timestamptz created_at
        timestamptz updated_at
    }

    TAGS {
        uuid id PK
        uuid user_id FK
        string name
        string color
        timestamptz created_at
    }

    EXPENSE_TAGS {
        uuid transaction_id FK
        uuid tag_id FK
    }

    BUDGETS {
        uuid id PK
        uuid user_id FK
        uuid category_id FK
        decimal amount_limit
        string period
        date start_date
        date end_date
        timestamptz created_at
    }

    USER_SETTINGS {
        uuid user_id PK
        string default_currency
        string language
        string theme
        bool notifications_enabled
        timestamptz updated_at
    }
```

### Обґрунтування нормалізації:
1. **1NF:** Усі атрибути атомарні; повторювані групи відсутні; множинний зв'язок тегів із транзакціями винесено в проміжну таблицю `expense_tags`.
2. **2NF:** Усі неключові атрибути повністю функціонально залежать від первинних ключів. У складеному ключі `expense_tags(transaction_id, tag_id)` атрибути залежать від усього ключа.
3. **3NF:** Відсутні транзитивні функціональні залежності. Наприклад, категорія зберігається окремо від транзакції, її назва й іконка не дублюються в рядках транзакцій.

---

## 3. Стратегія індексації (B-Tree Indexes)

Для гарантії часу відгуку $p95 \le 500$ мс під навантаженням створено такі індекси:

```sql
-- Швидкий пошук та авторизація за Telegram ID та Email
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Фільтрація та сортування журналу транзакцій користувача
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date DESC);
CREATE INDEX idx_transactions_user_date ON transactions(user_id, transaction_date DESC);
CREATE INDEX idx_transactions_user_type ON transactions(user_id, type);
CREATE INDEX idx_transactions_category ON transactions(category_id);

-- Категорії: швидке об'єднання системних та власних
CREATE INDEX idx_categories_user_id ON categories(user_id);
CREATE INDEX idx_categories_type ON categories(type);
```

---

## 4. Безпека даних: Row Level Security (RLS)

Усі таблиці мають активований механізм **Row Level Security (RLS)**:

```sql
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE budgets ENABLE ROW LEVEL SECURITY;

-- Політика ізоляції транзакцій:
CREATE POLICY "Users can only access their own transactions"
    ON transactions
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Політика для категорій:
CREATE POLICY "Users can access system and own categories"
    ON categories
    FOR SELECT
    USING (is_default = TRUE OR auth.uid() = user_id);
```

---

## 5. Міграції бази даних

Схема розгортається декларативно через SQL-міграції:
* [`sql/schema.sql`](file:///Users/mimi/Desktop/Antigravity/АтПпз/ExpenseTracker/sql/schema.sql) — повна початкова схема (таблиці, констрейнти `CHECK`, тригери `updated_at`, дефолтні категорії).
* [`sql/migration_001_add_user_fields.sql`](file:///Users/mimi/Desktop/Antigravity/АтПпз/ExpenseTracker/sql/migration_001_add_user_fields.sql) — міграція розширення профілю Telegram (`first_name`, `last_name`, `username`, `avatar_url`) та додаткових індексів.

---

## 6. Резервне копіювання та відновлення (Backup & Recovery)

1. **Point-In-Time Recovery (PITR):** Хмарна платформа Supabase веде безперервний журнал випереджувального запису (WAL), що дозволяє відновити стан БД до будь-якої секунди за останні 7 діб.
2. **Щоденні бекапи:** Автоматичні щоденні знімки (snapshot) зберігаються у зашифрованому S3-сховищі.
3. **Локальний аварійний експорт:** Дамп схеми та даних створюється командою:
   ```bash
   pg_dump -h db.supabase.co -U postgres -d postgres -F c -b -v -f backup_$(date +%Y%m%d).dump
   ```
