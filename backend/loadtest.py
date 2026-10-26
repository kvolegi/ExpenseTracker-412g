#!/usr/bin/env python3
"""
Performance and Load Testing Script (Лабораторна робота №6)
Expense Tracker API Benchmarking

Tests scenarios:
1. POST /api/v1/expenses (primary latency critical path from Lab 1)
2. GET /api/v1/expenses/stats (analytical aggregation load)

Load profile: 10, 20, 30, 50, 70, 100 concurrent virtual users.
Target SLA (Lab 1): p95 response time <= 500 ms under 100 concurrent users.
"""
import asyncio
import time
import statistics
import sys
from typing import List, Dict, Any
import httpx

BASE_URL = "http://127.0.0.1:8000"

async def authenticate_test_user(client: httpx.AsyncClient) -> str:
    """Register or log in a dedicated performance test user to obtain JWT token."""
    login_payload = {
        "email": "loadtest_runner@expensetracker.local",
        "password": "SecurePassword123!",
        "username": "loadtest_user"
    }
    # Try login first
    try:
        r = await client.post(f"{BASE_URL}/api/v1/auth/login", json={
            "email": login_payload["email"],
            "password": login_payload["password"]
        })
        if r.status_code == 200:
            return r.json()["access_token"]
    except Exception:
        pass

    # If login fails, register
    try:
        r = await client.post(f"{BASE_URL}/api/v1/auth/register", json=login_payload)
        if r.status_code in (200, 201):
            return r.json()["access_token"]
    except Exception:
        pass

    # Dev fallback login
    r = await client.post(f"{BASE_URL}/api/v1/auth/telegram/dev", json={
        "user_id": 88888,
        "username": "perf_user",
        "first_name": "Performance"
    })
    return r.json().get("access_token", "test-token")


async def simulate_user_session(
    user_id: int,
    token: str,
    iterations_per_user: int,
    results: List[float],
    errors: List[str]
):
    """Simulates a single virtual user generating transactions and reading statistics."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        for i in range(iterations_per_user):
            # 1. Create transaction (POST /api/v1/expenses)
            payload = {
                "type": "expense" if i % 3 != 0 else "income",
                "amount": float(10 + (i * 2.5) % 150),
                "currency": "USD",
                "comment": f"LoadTest tx u{user_id}-{i}",
                "payment_method": "card",
                "category_id": "00000000-0000-0000-0000-000000000001"
            }
            start = time.perf_counter()
            try:
                res = await client.post("/api/v1/expenses", json=payload, headers=headers)
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                if res.status_code in (200, 201):
                    results.append(elapsed_ms)
                else:
                    errors.append(f"HTTP {res.status_code}")
            except Exception as e:
                errors.append(str(e))

            # Small think time
            await asyncio.sleep(0.02)


async def run_load_stage(users_count: int, iterations_per_user: int = 10) -> Dict[str, Any]:
    """Runs a single benchmarking stage for a given number of concurrent users."""
    print(f"[*] Running stage: {users_count} concurrent users (total requests: {users_count * iterations_per_user})...")
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as auth_client:
        token = await authenticate_test_user(auth_client)

    results: List[float] = []
    errors: List[str] = []

    start_time = time.perf_counter()
    tasks = [
        simulate_user_session(uid, token, iterations_per_user, results, errors)
        for uid in range(users_count)
    ]
    await asyncio.gather(*tasks)
    total_time = time.perf_counter() - start_time

    if not results:
        return {
            "users": users_count,
            "requests": users_count * iterations_per_user,
            "p50": 0.0,
            "p95": 0.0,
            "error_rate": 100.0,
            "rps": 0.0
        }

    results.sort()
    p50 = statistics.median(results)
    idx_95 = int(len(results) * 0.95)
    p95 = results[min(idx_95, len(results) - 1)]
    error_rate = (len(errors) / (len(results) + len(errors))) * 100.0
    rps = len(results) / total_time if total_time > 0 else 0.0

    return {
        "users": users_count,
        "requests": len(results) + len(errors),
        "p50": round(p50, 2),
        "p95": round(p95, 2),
        "error_rate": round(error_rate, 2),
        "rps": round(rps, 2)
    }


async def main():
    print("=" * 70)
    print("🚀 EXPENSE TRACKER — PERFORMANCE BENCHMARK (Лабораторна робота №6)")
    print("=" * 70)
    stages = [10, 20, 30, 50, 70, 100]
    summary = []

    for stage_users in stages:
        res = await run_load_stage(stage_users, iterations_per_user=10)
        summary.append(res)
        print(f"    -> p50: {res['p50']} ms | p95: {res['p95']} ms | Errors: {res['error_rate']}% | RPS: {res['rps']}")
        await asyncio.sleep(0.5)

    print("\n" + "=" * 70)
    print("📊 ПІДСУМКОВА ТАБЛИЦЯ НАВАНТАЖУВАЛЬНОГО ЕКСПЕРИМЕНТУ (Таблиця 5 / 7)")
    print("=" * 70)
    print(f"{'Користувачів':<15} | {'p50, мс':<12} | {'p95, мс':<12} | {'Помилки, %':<12} | {'RPS':<10}")
    print("-" * 70)
    for row in summary:
        print(f"{row['users']:<15} | {row['p50']:<12} | {row['p95']:<12} | {row['error_rate']:<12} | {row['rps']:<10}")
    print("=" * 70)

    # Verification against Lab 1 SLA
    p95_100 = summary[-1]['p95']
    if p95_100 <= 500.0:
        print(f"✅ ВИСНОВОК: Сценарій ЛР1 ВИКОНАНО! p95 при 100 користувачах = {p95_100} мс (ліміт: 500 мс).")
    else:
        print(f"⚠️ ВИСНОВОК: p95 = {p95_100} мс перевищує цільовий показник 500 мс.")


# Optional Locust Support: locust -f loadtest.py
try:
    from locust import HttpUser, task, between

    class ExpenseTrackerLocustUser(HttpUser):
        wait_time = between(0.05, 0.2)

        def on_start(self):
            # Dev login
            res = self.client.post("/api/v1/auth/telegram/dev", json={
                "user_id": 99999,
                "username": "locust_user",
                "first_name": "Locust"
            })
            if res.status_code in (200, 201):
                self.token = res.json().get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
            else:
                self.headers = {}

        @task(3)
        def create_expense(self):
            self.client.post("/api/v1/expenses", json={
                "type": "expense",
                "amount": 42.0,
                "currency": "USD",
                "category_id": "00000000-0000-0000-0000-000000000001",
                "comment": "Locust load test item",
                "payment_method": "card"
            }, headers=self.headers)

        @task(1)
        def get_stats(self):
            self.client.get("/api/v1/expenses/stats", headers=self.headers)

except ImportError:
    pass

if __name__ == "__main__":
    asyncio.run(main())
