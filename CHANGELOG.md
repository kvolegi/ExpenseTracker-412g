# 📋 CHANGELOG — Журнал змін проєкту Expense Tracker

## [1.1.0] — 16.10.2026 (Лабораторна робота №3)
### Додано
- Патерни проєктування GoF у модулі `backend/src/patterns/patterns.py`:
  - **Factory Method:** `PaymentFactory` (`CashPayment`, `CardPayment`, `CryptoPayment`), `NotifierFactory` (`TelegramNotifier`, `EmailNotifier`).
  - **Builder:** `ExpenseBuilder` з покроковою валідацією полів та значень за замовчуванням.
  - **Strategy:** `SortStrategy` (`SortByDate`, `SortByAmount`, `SortByCategory`, `TransactionSorter`).
  - **Observer:** `EventBus` (`event_bus`) для публікації подій життєвого циклу транзакцій (`transaction.created`, `transaction.updated`, `transaction.deleted`).
  - **Facade:** `TransactionFacade` у шарі сервісів для об'єднання взаємодії між Builder, PaymentFactory, Repository, NotifierFactory та EventBus.
- Підписка обробників на події `EventBus` у точці входу `backend/main.py`.

## [1.0.0] — 11.10.2026 (Лабораторна робота №2)
### Додано
- Багатошарова архітектура ядра (Presentation, Application, Domain, Infrastructure).
- Специфікація REST API на FastAPI з 14 ендпоінтами та Swagger UI (`/docs`).
- Реляційна схема бази даних PostgreSQL у Supabase (`sql/schema.sql`) на 7 таблиць (3NF) з Row Level Security (RLS).
- Авторизація за email/паролем та валідація даних Telegram WebApp `initData`.
