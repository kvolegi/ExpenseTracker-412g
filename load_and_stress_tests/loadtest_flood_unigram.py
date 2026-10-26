"""
Навантажувальний тест Expense Tracker.
Запуск: python loadtest.py http://localhost:8000/api/v1 create <токен>
Сценарії: create (POST /expenses) або stats (GET /expenses/stats)
Токен тестового користувача можна також передати змінною середовища TOKEN.
Потрібно: pip install httpx
Скрипт пише тестові транзакції в базу, тому після тесту тестового користувача варто видалити.
"""
import asyncio
import os
import statistics
import sys
import time

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/api/v1"
SCENARIO = sys.argv[2] if len(sys.argv) > 2 else "create"
TOKEN = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("TOKEN", "")
LEVELS = [10, 20, 30, 50, 70, 100]
STEP_SECONDS = 60
SEED_COUNT = 500


async def prepare(client):
    if not TOKEN:
        sys.exit("Потрібен токен: python loadtest.py <адреса> <create|stats> <токен>")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    if SCENARIO == "stats":
        for _ in range(SEED_COUNT):
            await client.post(f"{BASE}/expenses", headers=headers,
                              json={"type": "expense", "amount": 10, "payment_method": "card"})
    return headers


async def worker(client, headers, stop_at, times, errors):
    while time.perf_counter() < stop_at:
        start = time.perf_counter()
        try:
            if SCENARIO == "create":
                r = await client.post(f"{BASE}/expenses", headers=headers,
                                      json={"type": "expense", "amount": 10, "payment_method": "card"})
            else:
                r = await client.get(f"{BASE}/expenses/stats", headers=headers)
            bad = r.status_code >= 400
        except Exception:
            bad = True
        times.append((time.perf_counter() - start) * 1000)
        errors.append(bad)


async def run_level(headers, users):
    times, errors = [], []
    limits = httpx.Limits(max_connections=users)
    async with httpx.AsyncClient(timeout=30, limits=limits) as client:
        stop_at = time.perf_counter() + STEP_SECONDS
        await asyncio.gather(*[worker(client, headers, stop_at, times, errors) for _ in range(users)])
    q = statistics.quantiles(times, n=100)
    return q[49], q[94], 100 * sum(errors) / len(errors), len(times)


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        headers = await prepare(client)
    print(f"Сценарій: {SCENARIO}, тривалість рівня: {STEP_SECONDS} с")
    print("користувачів | p50, мс | p95, мс | помилки, % | запитів")
    for users in LEVELS:
        p50, p95, err, n = await run_level(headers, users)
        print(f"{users:12d} | {p50:7.0f} | {p95:7.0f} | {err:10.1f} | {n}")


asyncio.run(main())
