# 📐 Архітектурна модель C4 (Лабораторна робота №8)

## 1. Загальний огляд
Для документування архітектури **Expense Tracker** використано підхід **C4 Model** (Context, Containers, Components). Діаграми структуровано за рівнями деталізації без змішування контекстів.

---

## 2. Зацікавлені сторони (Stakeholders — Таблиця 1)

| Зацікавлена сторона | Інтерес до системи | Найважливіший атрибут якості |
| :--- | :--- | :--- |
| **Кінцевий користувач** | Швидкий, простий облік витрат без паролів у звичному інтерфейсі Telegram | Зручність використання (Usability), Продуктивність (Performance) |
| **Команда розробників** | Модульність коду, простота додавання нових фіч та наочність патернів | Модифікованість (Maintainability), Тестованість (Testability) |
| **Викладач / Екзаменатор** | Відповідність архітектурним принципам, наявність GoF патернів, висока якість тестів і звітності | Архітектурна відповідність (Conformance), Документованість |
| **Хмарний хостинг (Railway / Supabase)** | Економічне споживання пам'яті та процесорного часу в межах безкоштовного тарифу | Ресурсоефективність (Efficiency), Надійність (Reliability) |
| **Екосистема Telegram** | Дотримання специфікації Telegram WebApp SDK, відсутність спаму та надійність Webhook | Безпека (Security), Сумісність (Interoperability) |

---

## 3. C4 Рівень 1 — Діаграма контексту системи (System Context)

Відображає систему як єдиний «чорний ящик» у взаємодії з користувачами та зовнішніми хмарними сервісами.

```mermaid
flowchart TD
    User(["👤 Користувач (Telegram User)"]):::person
    System["💰 Expense Tracker (Система обліку витрат)"]:::system
    Telegram["✈️ Telegram Bot Platform"]:::external
    Supabase["☁️ Supabase Cloud (PostgreSQL 16)"]:::external

    User -->|"Відкриває Mini App, вводить витрати"| System
    User -->|"Спілкується з ботом, надсилає команди"| Telegram
    Telegram -->|"Передає підписані initData у Webview"| System
    System -->|"Надсилає push-сповіщення про транзакції"| Telegram
    System -->|"Зберігає транзакції, читає категорії"| Supabase

    classDef person fill:#08427B,stroke:#052e56,color:#fff;
    classDef system fill:#1168BD,stroke:#0b4884,color:#fff;
    classDef external fill:#999999,stroke:#666666,color:#fff;
```

---

## 4. C4 Рівень 2 — Діаграма контейнерів (Container Diagram)

Показує розгортання системи у вигляді окремих виконуваних контейнерів та протоколи взаємодії.

```mermaid
flowchart TD
    User(["👤 Користувач"]):::person

    subgraph Boundaries ["Expense Tracker System Boundaries"]
        Frontend["📱 Single Page Application (Mini App)\n[HTML5, CSS3, Vanilla JS, Telegram SDK]\nПорт: 3000"]:::container
        StaticServer["🌐 Frontend Static Server\n[Python 3.12, server.py]\nRailway / Localhost"]:::container
        BackendAPI["⚙️ Backend REST API\n[Python 3.12, FastAPI 0.111, Uvicorn]\nПорт: 8000"]:::container
    end

    TelegramAPI["✈️ Telegram Bot API\n[Хмарний сервіс Telegram]"]:::external
    Database[("🗄️ Database\n[PostgreSQL 16, Supabase Cloud]\nRLS, B-Tree Indexes")]:::database

    User -->|"Взаємодіє з інтерфейсом"| Frontend
    StaticServer -->|"Віддає статичні файли (SPA)"| Frontend
    Frontend -->|"REST API запити: JSON / HTTPS\nЗаголовок: Bearer JWT"| BackendAPI
    BackendAPI -->|"SQL / PostgreSQL Wire Protocol over TLS"| Database
    BackendAPI -->|"Фонові сповіщення про витрати: HTTPS POST"| TelegramAPI

    classDef person fill:#08427B,stroke:#052e56,color:#fff;
    classDef container fill:#438DD5,stroke:#2e6295,color:#fff;
    classDef database fill:#1168BD,stroke:#0b4884,color:#fff;
    classDef external fill:#999999,stroke:#666666,color:#fff;
```

---

## 5. C4 Рівень 3 — Діаграма компонентів бекенду (Component Diagram)

Розкриває внутрішню структуру контейнера `Backend API` та 4-рівневу архітектуру **Modular Monolith**:

```mermaid
flowchart TD
    subgraph PresentationLayer ["1. Presentation Layer (API Routers)"]
        AuthRouter["auth_router\n(/api/v1/auth)"]:::component
        TxRouter["tx_router\n(/api/v1/expenses)"]:::component
        CatRouter["cat_router\n(/api/v1/categories)"]:::component
    end

    subgraph SecurityCore ["Core & Cross-Cutting"]
        Security["security.py\n(JWT, bcrypt, verify_init_data)"]:::core
        Config["config.py\n(Settings Singleton)"]:::core
        Logger["logger.py\n(Structured JSON Logger)"]:::core
    end

    subgraph BusinessLayer ["2. Business Logic Layer (Services & Patterns)"]
        AuthService["AuthService\n(Session management)"]:::service
        TxFacade["TransactionFacade (Facade Pattern)\n(Orchestrates transaction lifecycle)"]:::service
        CatService["CategoryService\n(Category catalog)"]:::service
        Patterns["patterns.py\n(Builder, Factory, Strategy, Observer)"]:::pattern
        BackgroundTasks["background.py\n(Async Notifications)"]:::service
    end

    subgraph DataAccessLayer ["3. Data Access Layer (Repositories)"]
        UserRepo["UserRepository\n(users table)"]:::repo
        TxRepo["TransactionRepository\n(transactions table)"]:::repo
        CatRepo["CategoryRepository\n(categories table)"]:::repo
    end

    subgraph DatabaseLayer ["4. Database Access Client"]
        DBClient["database.py\n(Supabase Client & Local Fallback)"]:::db
    end

    AuthRouter --> Security
    AuthRouter --> AuthService
    TxRouter --> Security
    TxRouter --> TxFacade
    CatRouter --> Security
    CatRouter --> CatService

    TxFacade --> Patterns
    TxFacade --> BackgroundTasks
    TxFacade --> TxRepo
    AuthService --> UserRepo
    CatService --> CatRepo

    UserRepo --> DBClient
    TxRepo --> DBClient
    CatRepo --> DBClient

    classDef component fill:#85BBF0,stroke:#5d82a8,color:#000;
    classDef core fill:#FFE6CC,stroke:#D79B00,color:#000;
    classDef service fill:#D5E8D4,stroke:#82B366,color:#000;
    classDef pattern fill:#E1D5E7,stroke:#9673A6,color:#000;
    classDef repo fill:#FFF2CC,stroke:#D6B656,color:#000;
    classDef db fill:#F8CECC,stroke:#B85450,color:#000;
```

---

## 6. Глосарій предметної області (Domain Glossary — Таблиця 2)

| Термін | Семантичне значення у системі |
| :--- | :--- |
| **Transaction (Транзакція)** | Фіксація фінансової операції: дохід (`income`) або витрата (`expense`) із зазначенням суми, валюти, дати, категорії та способу оплати. |
| **Category (Категорія)** | Класифікатор транзакцій (наприклад, 🍔 Food, 🚗 Transport). Поділяється на системні (`is_default = true`) та користувацькі. |
| **Telegram Mini App (TMA)** | Клієнтський веб-додаток, інтегрований у месенджер Telegram через Webview та WebApp SDK. |
| **initData** | Криптографічно підписаний рядок даних користувача, який Telegram передає клієнту під час відкриття Mini App. |
| **TransactionFacade** | Сервіс бізнес-логіки (патерн Facade), що забезпечує єдину точку входу для створення транзакцій, виклику Builder, платіжних фабрик та шини подій. |
| **Row Level Security (RLS)** | Механізм безпеки PostgreSQL на рівні рядків таблиці, що запобігає витоку даних між користувачами. |
| **PaymentMethod** | Спосіб здійснення фінансової операції: готівка (`cash`), картка (`card`), криптовалюта (`crypto`). |
| **EventBus** | Реалізація шаблону Observer у пам'яті додатку для розсилки подій (`transaction.created`) підписникам. |
| **Modular Monolith** | Архітектурний стиль побудови бекенду: монолітна кодова база, розділена на чіткі слабозв'язані шари (Layers). |
