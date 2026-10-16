# 💰 Expense Tracker — Наскрізний проєкт

> Telegram Mini App для обліку персональних та спільних фінансів.

## Команда розробників (ОНЮА, Кафедра кібербезпеки, група ІПЗ-42)
* **Чугунникова Вікторія Ігорівна** — Аналітик домену / DBA
* **Петрушенко Мілєна Романівна** — Системний архітектор / Team Lead
* **Бевзюк Єгор Сергійович** — Інженер з якості / UI Lead

## Архітектурний розвиток проєкту за лабораторними роботами

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
* **Породжувальні:** `PaymentFactory`, `NotifierFactory`, `ExpenseBuilder`.
* **Поведінкові:** `SortStrategy` (`SortByDate`, `SortByAmount`, `SortByCategory`), `EventBus` (`event_bus`).
* **Структурні:** `TransactionFacade` у шарі застосунку.
* [Детальний опис патернів та метрик рефакторингу](docs/patterns.md).
* [Журнал змін проєкту](CHANGELOG.md).

## Ліцензія
[MIT License](LICENSE) © 2026 Чугунникова В.І., Петрушенко М.Р., Бевзюк Є.С.
