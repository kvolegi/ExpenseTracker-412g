# 🧪 Набір скриптів навантажувального, стрес- та негативного тестування

Ця папка містить повний набір виконуваних скриптів, тестових інструментів та сирих вихідних даних (JSON), які використовувалися під час дослідження надійності, стійкості до відмов та порівняльного аналізу інстансу **Self-Hosted (Coolify)** проти **Cloud (Supabase / Railway)**.

Детальний аналітичний звіт з висновками та графіками розміщено у файлі [`../docs/STRESS_TEST_REPORT.md`](../docs/STRESS_TEST_REPORT.md).

---

## 📁 Склад каталогу

### 1. Скрипти бенчмаркінгу та навантаження
* [`benchmark_coolify.py`](benchmark_coolify.py) — Багатостадійний асинхронний стрес-тест бекенду в Coolify (`https://api-tracker.samzhoserv.duckdns.org`). Генерує конкурентні запити з автентифікацією від 10 до 500 віртуальних користувачів (VU), вимірює RPS, p50, p95, p99 та фіксує точки відмови Traefik і Uvicorn.
* [`benchmark_supabase.py`](benchmark_supabase.py) — Навантажувальний тест нативного PostgREST API Supabase Cloud (`https://uwxqsilckhtpwjxztfio.supabase.co`). Проводить заміри швидкодії рушія бази даних до 150 VU.
* [`loadtest_flood_unigram.py`](loadtest_flood_unigram.py) — Навчальний flood-скрипт випробувань без штучних затримок (`think-time`), надісланий для лабораторної роботи, який штурмує ендпоінти `POST /expenses` та `GET /expenses/stats`.
* [`test_api.py`](test_api.py) — Скрипт функціональної димової перевірки (smoke test) та валідації життєвого циклу сутностей API (створення користувача, генерація JWT, додавання транзакції, отримання статистики).

### 2. Скрипти негативного тестування, фаззингу та відмови
* [`fuzz_and_crash_coolify.py`](fuzz_and_crash_coolify.py) — Комплексний набір негативних тестів та спроб доведення модулів до відмови:
  1. *Відсутня автентифікація* (401 Unauthorized).
  2. *Підроблений JWT токен* (401 Unauthorized).
  3. *SQL Injection* у коментарях та полях пошуку.
  4. *Stored XSS* у полях опису транзакцій.
  5. *Від'ємні суми транзакцій* (перевірка валідатора).
  6. *Гігантські числові суми* (Numeric Overflow).
  7. *Неіснуючий Foreign Key `category_id`* (перевірка реляційної цілісності).
  8. *Некоректний UUID-формат*.
  9. *Memory Bomb (10 МБ корисного навантаження у JSON)*.
  10. *Unicode/Emoji Bomb (200 000 символів)*.
  11. *Пул-стрес локального PostgreSQL (вибивання ліміту max_connections)*.
  12. *Стрес фронтенд-проксі сервера* на `https://tracker.samzhoserv.duckdns.org`.

### 3. Сирі результати вимірювань (Raw Data)
* [`coolify_stress_results.json`](coolify_stress_results.json) — Повні логи затримок, квантилів та помилок стрес-тесту Coolify (10..500 VU).
* [`supabase_stress_results.json`](supabase_stress_results.json) — Повні логи навантаження Supabase PostgREST (10..150 VU).
* [`coolify_negative_results.json`](coolify_negative_results.json) — Детальні статуси відповідей та корисні навантаження кожного негативного тесту.
* [`loadtest_chart.png`](loadtest_chart.png) — Згенерований порівняльний графік латентності p50/p95 за рівнями навантаження із лінією SLA 500 мс.

---

## 🚀 Як запустити тести повторно

Встановіть залежності:
```bash
pip install httpx psycopg2-binary
```

Запуск стрес-тесту Coolify:
```bash
python benchmark_coolify.py
```

Запуск фаззингу та негативних тестів:
```bash
python fuzz_and_crash_coolify.py
```

Запуск бенчмарку Supabase:
```bash
python benchmark_supabase.py
```
