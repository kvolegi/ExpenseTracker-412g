import asyncio
import time
import statistics
import json
import httpx

BASE_URL = "https://api-tracker.samzhoserv.duckdns.org/api/v1"

async def get_auth_token():
    async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
        r = await client.post(f"{BASE_URL}/auth/telegram/dev", json={
            "user_id": 777777,
            "username": "stress_runner",
            "first_name": "Stress"
        })
        return r.json()["access_token"]

async def worker(token: str, num_requests: int, results: list, errors: dict):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    limits = httpx.Limits(max_keepalive_connections=50, max_connections=100)
    async with httpx.AsyncClient(verify=False, timeout=15.0, limits=limits) as client:
        for i in range(num_requests):
            t0 = time.perf_counter()
            try:
                # Alternating POST and GET
                if i % 2 == 0:
                    payload = {
                        "type": "expense",
                        "amount": 25.50,
                        "currency": "USD",
                        "comment": f"Stress load item {i}",
                        "payment_method": "card"
                    }
                    res = await client.post(f"{BASE_URL}/expenses", json=payload, headers=headers)
                else:
                    res = await client.get(f"{BASE_URL}/expenses/stats", headers=headers)

                lat = (time.perf_counter() - t0) * 1000.0
                if res.status_code in (200, 201):
                    results.append(lat)
                else:
                    status = res.status_code
                    errors[status] = errors.get(status, 0) + 1
            except Exception as e:
                err_type = type(e).__name__
                errors[err_type] = errors.get(err_type, 0) + 1

async def run_stage(concurrency: int, total_requests: int, token: str):
    req_per_worker = total_requests // concurrency
    results = []
    errors = {}
    
    t_start = time.perf_counter()
    tasks = [worker(token, req_per_worker, results, errors) for _ in range(concurrency)]
    await asyncio.gather(*tasks)
    duration = time.perf_counter() - t_start
    
    total_completed = len(results) + sum(errors.values())
    p50 = statistics.median(results) if results else 0
    p95 = statistics.quantiles(results, n=100)[94] if len(results) >= 100 else (max(results) if results else 0)
    p99 = statistics.quantiles(results, n=100)[98] if len(results) >= 100 else (max(results) if results else 0)
    rps = total_completed / duration if duration > 0 else 0
    err_count = sum(errors.values())
    err_rate = (err_count / total_completed * 100.0) if total_completed > 0 else 0
    
    print(f"[Concurrency {concurrency:4d}] Total: {total_completed:5d} | Success: {len(results):5d} | Err: {err_count:4d} ({err_rate:5.1f}%) | RPS: {rps:6.1f} | p50: {p50:6.1f}ms | p95: {p95:6.1f}ms | p99: {p99:6.1f}ms | Errors breakdown: {errors}")
    return {
        "concurrency": concurrency,
        "total": total_completed,
        "success": len(results),
        "errors": err_count,
        "error_rate": err_rate,
        "rps": round(rps, 1),
        "p50": round(p50, 1),
        "p95": round(p95, 1),
        "p99": round(p99, 1),
        "errors_detail": errors,
        "duration": round(duration, 2)
    }

async def main():
    print("=== STARTING COOLIFY SELF-HOSTED API STRESS TEST ===")
    token = await get_auth_token()
    stages = [
        (10, 200),
        (25, 500),
        (50, 1000),
        (100, 2000),
        (200, 3000),
        (350, 3500),
        (500, 5000),
    ]
    summary = []
    for c, n in stages:
        res = await run_stage(c, n, token)
        summary.append(res)
        await asyncio.sleep(2)
        
    with open("coolify_stress_results.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("=== COMPLETED COOLIFY STRESS TEST ===")

if __name__ == "__main__":
    asyncio.run(main())
