# 📋 CHANGELOG — Журнал змін проєкту Expense Tracker

## [1.6.0] — 26.10.2026 (Лабораторна робота №8 — Фінальний захист проєкту v1.0.0 Final)
### Додано
- Повна архітектурна модель **C4 Model** у документі [`docs/c4-model.md`](docs/c4-model.md):
  - Рівень 1: System Context Diagram (взаємодія з Telegram та Supabase).
  - Рівень 2: Container Diagram (Frontend SPA, Backend REST API, PostgreSQL).
  - Рівень 3: Component Diagram (Routers, Security, Facade, Patterns, Repositories, Database Client).
- Реєстр технічного боргу та компромісів із планом рефакторингу ([`docs/technical-debt.md`](docs/technical-debt.md)).
- Матриця верифікації сценаріїв якості ЛР1 ([`docs/quality-verification.md`](docs/quality-verification.md)).
- Розрахунок метрик кодової бази (Radon, Halstead, Maintainability Index) у каталозі [`backend/docs/metrics/`](backend/docs/metrics/).
- Посібник для захисту перед екзаменатором із відповідями на типові запитання ([`docs/defense-guide.md`](docs/defense-guide.md)).
- Оновлено фінальний `README.md` із бейджами CI, покриттям 59%, архітектурними схемами та довідником API.

## [1.5.0] — 25.10.2026 (Лабораторна робота №7 — Тестування архітектури та CI/CD)
### Додано
- Повний набір із 37 автоматизованих тестів на базі `pytest` у каталозі `backend/tests/`:
  - 10 тестів схем валідації Pydantic (`test_validators.py`).
  - 5 тестів бізнес-логіки сервісу `TransactionFacade` (`test_services.py`).
  - 3 тести розрахунку балансу за TDD (`test_balance.py`).
  - 6 інтеграційних тестів репозиторіїв з Mock-клієнтом Supabase (`test_repository.py`).
  - 13 тестів ієрархії винятків `AppError` та `ExpenseValidator` (`test_exceptions.py`).
- Досягнуто сумарне покриття коду тестами **59%** (при нормативі курсу не нижче 50%).
- Конфігурація конвеєра неперервної інтеграції GitHub Actions ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) для автоматичного запуску тестів та збірки Docker-образу.
- Контейнеризація бекенду: `Dockerfile` та `docker-compose.yml`.
- Документація піраміди тестування та матриці правил ([`docs/architecture-testing.md`](docs/architecture-testing.md)).

## [1.4.0] — 24.10.2026 (Лабораторна робота №6 — Безпека та продуктивність)
### Додано
- Аналіз меж довіри та модель загроз за методологією **STRIDE** на 10 векторів атак ([`docs/security-and-performance.md`](docs/security-and-performance.md)).
- Криптографічна автентифікація: перевірка Telegram `initData` через HMAC-SHA256, випуск та верифікація токенів JWT (HS256), хешування паролів `bcrypt`.
- Матриця прав доступу (Access Control Matrix) та гарантія відсутності витоку чужих даних.
- Асинхронний скрипт навантажувального бенчмаркінгу [`backend/loadtest.py`](backend/loadtest.py) для рівнів 10, 20, 30, 50, 70, 100 одночасних користувачів.
- Експериментальне підтвердження SLA з ЛР1: $p95 = 198.4$ мс при 100 користувачах (ліміт: 500 мс) із 0.0% помилок.

## [1.3.0] — 22.10.2026 (Лабораторна робота №5 — Архітектура даних та сховища)
### Додано
- Реляційна схема даних у PostgreSQL 16 (Supabase) у 3NF нормальній формі ([`docs/database-architecture.md`](docs/database-architecture.md)).
- Файл міграції [`sql/migration_001_add_user_fields.sql`](sql/migration_001_add_user_fields.sql) для полів профілю Telegram (`first_name`, `last_name`, `username`, `avatar_url`).
- Створення B-Tree індексів на ключових зовнішніх ключах і полях пошуку/фільтрації.
- Активація політик Row Level Security (RLS) для гарантованої ізоляції записів користувачів.
- Стратегія аварійного резервного копіювання (PITR та щоденні дампи `pg_dump`).

## [1.2.0] — 20.10.2026 (Лабораторна робота №4 — Клієнтська частина)
### Додано
- Клієнтська частина: Telegram Mini App на чистому HTML/CSS/Vanilla JS (`frontend/index.html`).
- Клієнтський шар сервісів `api.js` (`ApiService`, `Logger`, `EventBus`, `ExpenseBuilder`).
- Автономний статичний сервер `server.py` з реверс-проксі до REST API на порті 3000.
- Конфігурація розгортання `railway.toml`.
- Екрани: Splash Screen, Login (Telegram Auth), Home (Баланс, список транзакцій), Overview (тижневі графіки), Profile.

## [1.1.0] — 16.10.2026 (Лабораторна робота №3 — Патерни проєктування GoF)
### Додано
- GoF патерни в `backend/src/patterns/patterns.py`: Factory Method (`PaymentFactory`, `NotifierFactory`), Builder (`ExpenseBuilder`), Strategy (`TransactionSorter`), Observer (`EventBus`), Facade (`TransactionFacade`).
- Публікація та підписка на події в точці входу `backend/main.py`.

## [1.0.0] — 11.10.2026 (Лабораторна робота №2 — Багатошарове ядро)
### Додано
- 4-шарова архітектура ядра (Presentation, Application, Domain, Infrastructure).
- Специфікація REST API на FastAPI з 14 ендпоінтами та Swagger UI (`/docs`).
- Реляційна схема бази даних PostgreSQL у Supabase (`sql/schema.sql`).

## [0.1.0] — 05.10.2026 (Лабораторна робота №1 — Архітектурний контекст)
### Додано
- Початкова структура репозиторію та документація: ADR-001 (Modular Monolith), ADR-002 (Technology Stack), доменний глосарій, сценарії якості, ліцензія MIT.
