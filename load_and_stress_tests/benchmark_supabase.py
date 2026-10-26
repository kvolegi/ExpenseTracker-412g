import asyncio
import time
import statistics
import json
import httpx

SUPABASE_URL = "https://uwxqsilckhtpwjxztfio.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

async def worker(num_requests: int, results: list, errors: dict):
    limits = httpx.Limits(max_keepalive_connections=50, max_connections=100)
    async with httpx.AsyncClient(verify=False, timeout=15.0, limits=limits) as client:
        for i in range(num_requests):
            t0 = time.perf_counter()
            try:
                if i % 2 == 0:
                    payload = {
                        "user_id": "fb6b061d-2dbf-458f-b7b7-a1b7284d27ee",
                        "type": "expense",
                        "amount": 25.50,
                        "currency": "USD",
                        "comment": f"Supabase benchmark item {i}",
                        "payment_method": "card"
                    }
                    res = await client.post(f"{SUPABASE_URL}/rest/v1/transactions", json=payload, headers=headers)
                else:
                    res = await client.get(f"{SUPABASE_URL}/rest/v1/transactions?select=*&limit=50", headers=headers)

                lat = (time.perf_counter() - t0) * 1000.0
                if res.status_code in (200, 201):
                    results.append(lat)
                else:
                    status = res.status_code
                    errors[status] = errors.get(status, 0) + 1
            except Exception as e:
                err_type = type(e).__name__
                errors[err_type] = errors.get(err_type, 0) + 1

async def run_stage(concurrency: int, total_requests: int):
    req_per_worker = total_requests // concurrency
    results = []
    errors = {}
    
    t_start = time.perf_counter()
    tasks = [worker(req_per_worker, results, errors) for _ in range(concurrency)]
    await asyncio.gather(*tasks)
    duration = time.perf_counter() - t_start
    
    total_completed = len(results) + sum(errors.values())
    p50 = statistics.median(results) if results else 0
    p95 = statistics.quantiles(results, n=100)[94] if len(results) >= 100 else (max(results) if results else 0)
    p99 = statistics.quantiles(results, n=100)[98] if len(results) >= 100 else (max(results) if results else 0)
    rps = total_completed / duration if duration > 0 else 0
    err_count = sum(errors.values())
    err_rate = (err_count / total_completed * 100.0) if total_completed > 0 else 0
    
    print(f"[Supabase Concurrency {concurrency:4d}] Total: {total_completed:5d} | Success: {len(results):5d} | Err: {err_count:4d} ({err_rate:5.1f}%) | RPS: {rps:6.1f} | p50: {p50:6.1f}ms | p95: {p95:6.1f}ms | p99: {p99:6.1f}ms | Errors breakdown: {errors}")
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
    print("=== STARTING SUPABASE CLOUD BENCHMARK ===")
    stages = [
        (10, 100),
        (25, 250),
        (50, 500),
        (100, 1000),
        (150, 1500),
    ]
    summary = []
    for c, n in stages:
        res = await run_stage(c, n)
        summary.append(res)
        await asyncio.sleep(2)
        
    with open("supabase_stress_results.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("=== COMPLETED SUPABASE BENCHMARK ===")

if __name__ == "__main__":
    asyncio.run(main())
