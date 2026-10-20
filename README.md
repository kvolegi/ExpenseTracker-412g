# 💰 Expense Tracker — Наскрізний проєкт

> Telegram Mini App для обліку персональних та спільних фінансів.

## Команда розробників (ОНЮА, Кафедра кібербезпеки, група ІПЗ-42)
* **Чугунникова Вікторія Ігорівна** — Аналітик домену / DBA
* **Петрушенко Мілєна Романівна** — Системний архітектор / Team Lead
* **Бевзюк Єгор Сергійович** — Інженер з якості / UI Lead

## Еволюція архітектури за лабораторними роботами

### 🏷️ Лабораторна робота №1: Архітектурний контекст та вибір стилю
* [ADR-001: Вибір архітектурного стилю](docs/adr/ADR-001-architectural-style.md) (Модульний моноліт)
* [ADR-002: Вибір технологічного стека](docs/adr/ADR-002-technology-stack.md) (FastAPI + Supabase + Vanilla JS)
* [Глосарій домену](docs/glossary.md) та [Сценарії атрибутів якості](docs/quality-scenarios.md)
* [C4 Context Diagram Level 1](docs/c4-context.md)

### 🏷️ Лабораторна робота №2: Багатошарове ядро системи
* 4 горизонтальні шари: Presentation (`routers.py`), Application (`services.py`), Domain (`schemas.py`, `expense_validator.py`), Infrastructure (`repositories.py`, `database.py`).
* Реляційна схема PostgreSQL (`sql/schema.sql`) на 7 таблиць (3NF) з Row Level Security (RLS).
* [Доменна модель класів](docs/domain-class-diagram.md).
* [Оцінка сценаріїв якості](docs/QUALITY_ASSESSMENT.md).

### 🏷️ Лабораторна робота №3: Патерни проєктування (GoF)
* **Породжувальні:** `PaymentFactory` (комісії платежів), `NotifierFactory`, `ExpenseBuilder` (покрокова збірка транзакції).
* **Поведінкові:** `SortStrategy` (`SortByDate`, `SortByAmount`, `SortByCategory`), `EventBus` (`event_bus`).
* **Структурні:** `TransactionFacade` у шарі застосунку.
* [Детальний опис патернів та метрик рефакторингу](docs/patterns.md).

### 🏷️ Лабораторна робота №4: Розробка клієнтської частини застосунку
* Клієнтська частина: **Telegram Mini App** на чистому стеку (HTML5 / CSS3 / Vanilla JS) у каталозі `frontend/`.
* Клієнтський сервісний шар: `frontend/api.js` (`ApiService`, `Logger`, `EventBus`, `ExpenseBuilder`).
* Автономний сервер `frontend/server.py` та конфігурація розгортання `frontend/railway.toml`.
* Екрани: Splash, Login (Telegram Auth), Home (Баланс, список транзакцій), Overview (Тижневий графік витрат), Profile.
* [Архітектура клієнтської частини та навігаційні потоки](docs/frontend-architecture.md).
* [Журнал версій та змін проєкту](CHANGELOG.md).

## Швидкий запуск
1. Запуск бекенду: `cd backend && uvicorn main:app --reload` (порт 8000, Swagger на `/docs`).
2. Запуск фронтенду: `cd frontend && python server.py` (порт 3000, Mini App на `http://localhost:3000`).

## Ліцензія
[MIT License](LICENSE) © 2026 Чугунникова В.І., Петрушенко М.Р., Бевзюк Є.С.
