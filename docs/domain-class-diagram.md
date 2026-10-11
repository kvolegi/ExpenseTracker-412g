# Доменна модель системи (ЛР 2)

## Основні сутності домену:
1. **User:** id, telegram_id, email, password_hash, username, first_name, last_name, avatar_url.
2. **Category:** id, user_id (null для системних), name, icon, color, type (income, expense, both), is_default.
3. **Transaction:** id, user_id, category_id, type, amount, currency, comment, payment_method, transaction_date.
4. **Tag:** id, user_id, name, color.
5. **Budget:** id, user_id, category_id, amount, period (weekly, monthly, yearly), start_date, end_date, is_active.

Зв'язок транзакцій і тегів (M:N) реалізовано через проміжну таблицю `expense_tags`.
