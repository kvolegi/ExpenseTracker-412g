# 💰 Expense Tracker — Наскрізний проєкт

> Telegram Mini App для обліку персональних та спільних фінансів.

## Команда розробників (ОНЮА, Кафедра кібербезпеки, група ІПЗ-42)
* **Чугунникова Вікторія Ігорівна** — Аналітик домену (БД `sql/schema.sql`, ER-модель, репозиторії)
* **Петрушенко Мілєна Романівна** — Системний архітектор (Багатошарова структура `src/`, REST API, ADR-001, ADR-002)
* **Бевзюк Єгор Сергійович** — Інженер з якості (Сценарії якості, C4 контекст, доменна модель)

## Багатошарова структура ядра (Лабораторна робота №2)
* **Шар подання (Presentation):** `backend/src/api/routers.py`, `backend/main.py` (FastAPI REST-ендпоінти з інтерактивною документацією Swagger UI на `/docs`)
* **Шар застосунку (Application):** `backend/src/services/services.py` (`TransactionService`, `AuthService`, `CategoryService` — реалізація ключових сценаріїв використання)
* **Доменний шар (Domain):** `backend/src/models/schemas.py`, `backend/src/validators/expense_validator.py` (Pydantic-схеми, доменні інваріанти)
* **Інфраструктурний шар (Infrastructure):** `backend/src/repositories/repositories.py`, `backend/src/core/database.py` (Data Access Layer)
* **Наскрізні модулі:** `backend/src/core/config.py`, `backend/src/core/logger.py`, `backend/src/core/security.py`

*Примітка:* Клієнтський інтерфейс (Telegram Mini App) та GoF-патерни проєктування виділені для реалізації в наступних лабораторних роботах (ЛР 3–4).

## База даних
* `sql/schema.sql` — реляційна схема з 7 таблиць (`users`, `categories`, `transactions`, `tags`, `expense_tags`, `budgets`, `user_settings`) з нормалізацією 3NF та Row Level Security (RLS).

## Архітектурна документація (ADR)
* [ADR-001: Вибір архітектурного стилю](docs/adr/ADR-001-architectural-style.md) (Модульний моноліт)
* [ADR-002: Вибір технологічного стека](docs/adr/ADR-002-technology-stack.md) (FastAPI + Supabase + Vanilla JS)
* [Глосарій домену та зацікавлені сторони](docs/glossary.md)
* [Сценарії атрибутів якості](docs/quality-scenarios.md)
* [C4 Context Diagram Level 1](docs/c4-context.md)
* [Доменна модель класів](docs/domain-class-diagram.md)

## Ліцензія
[MIT License](LICENSE) © 2026 Чугунникова В.І., Петрушенко М.Р., Бевзюк Є.С.
