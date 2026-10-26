import asyncio
import httpx
import json
import uuid

BASE_URL = "https://api-tracker.samzhoserv.duckdns.org/api/v1"

async def get_token():
    async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
        r = await client.post(f"{BASE_URL}/auth/telegram/dev", json={
            "user_id": 12345,
            "username": "fuzz_tester",
            "first_name": "Fuzzer"
        })
        return r.json()["access_token"]

async def run_negative_tests():
    token = await get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    test_results = []
    
    async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
        # Test 1: Negative Amount
        print("[*] Test 1: Negative amount (-150.00)")
        r1 = await client.post(f"{BASE_URL}/expenses", json={"type": "expense", "amount": -150.00}, headers=headers)
        test_results.append({"test": "Negative amount (-150.00)", "status": r1.status_code, "body": r1.text[:200]})
        
        # Test 2: Zero Amount
        print("[*] Test 2: Zero amount (0.00)")
        r2 = await client.post(f"{BASE_URL}/expenses", json={"type": "expense", "amount": 0.00}, headers=headers)
        test_results.append({"test": "Zero amount (0.00)", "status": r2.status_code, "body": r2.text[:200]})

        # Test 3: String NaN / Infinity
        print("[*] Test 3: String 'Infinity' amount")
        r3 = await client.post(f"{BASE_URL}/expenses", json={"type": "expense", "amount": "Infinity"}, headers=headers)
        test_results.append({"test": "String 'Infinity' amount", "status": r3.status_code, "body": r3.text[:200]})

        # Test 4: Huge Exponent Float (1e308)
        print("[*] Test 4: Huge float (1e308)")
        r4 = await client.post(f"{BASE_URL}/expenses", json={"type": "expense", "amount": 1e308}, headers=headers)
        test_results.append({"test": "Huge float (1e308)", "status": r4.status_code, "body": r4.text[:200]})

        # Test 5: Invalid Category UUID format
        print("[*] Test 5: Invalid category UUID format")
        r5 = await client.post(f"{BASE_URL}/expenses", json={"type": "expense", "amount": 100, "category_id": "not-a-valid-uuid-123"}, headers=headers)
        test_results.append({"test": "Invalid category UUID format", "status": r5.status_code, "body": r5.text[:200]})

        # Test 6: Non-existent Category UUID
        print("[*] Test 6: Non-existent Category UUID")
        r6 = await client.post(f"{BASE_URL}/expenses", json={"type": "expense", "amount": 100, "category_id": "ffffffff-ffff-ffff-ffff-ffffffffffff"}, headers=headers)
        test_results.append({"test": "Non-existent Category UUID", "status": r6.status_code, "body": r6.text[:200]})

        # Test 7: SQL Injection Payload in comment
        print("[*] Test 7: SQL Injection in comment")
        sqli_comment = "'); DROP TABLE transactions; SELECT * FROM users WHERE ('1'='1"
        r7 = await client.post(f"{BASE_URL}/expenses", json={"type": "expense", "amount": 50, "comment": sqli_comment}, headers=headers)
        test_results.append({"test": "SQL Injection payload in comment", "status": r7.status_code, "body": r7.text[:200]})

        # Test 8: Stored XSS Script Payload
        print("[*] Test 8: XSS Script payload in comment")
        xss_comment = "<script>alert('XSS_ATTACK_VECTOR_' + document.cookie);</script><img src=x onerror=alert(1)>"
        r8 = await client.post(f"{BASE_URL}/expenses", json={"type": "expense", "amount": 75, "comment": xss_comment}, headers=headers)
        test_results.append({"test": "XSS Script payload in comment", "status": r8.status_code, "body": r8.text[:200]})

        # Test 9: Unicode Bomb / 200,000 emojis (Buffer / Memory Stress)
        print("[*] Test 9: 200,000 emojis in comment field (~800 KB)")
        emoji_bomb = "💸💥🔥💣" * 50000
        r9 = await client.post(f"{BASE_URL}/expenses", json={"type": "expense", "amount": 10, "comment": emoji_bomb}, headers=headers)
        test_results.append({"test": "200,000 emojis in comment (~800 KB)", "status": r9.status_code, "body": r9.text[:200]})

        # Test 10: 10 MB Payload Attack (Oversized Request)
        print("[*] Test 10: 10 MB massive payload")
        ten_mb_str = "A" * (10 * 1024 * 1024)
        try:
            r10 = await client.post(f"{BASE_URL}/expenses", json={"type": "expense", "amount": 10, "comment": ten_mb_str}, headers=headers)
            test_results.append({"test": "10 MB massive payload", "status": r10.status_code, "body": r10.text[:200]})
        except Exception as e:
            test_results.append({"test": "10 MB massive payload", "status": "EXCEPTION", "body": str(e)})

        # Test 11: JWT Alg None Attack
        print("[*] Test 11: JWT Alg: none attack")
        import base64
        header_b64 = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(b'{"sub":"fake_user_id","exp":9999999999}').decode().rstrip("=")
        fake_jwt = f"{header_b64}.{payload_b64}."
        r11 = await client.get(f"{BASE_URL}/expenses", headers={"Authorization": f"Bearer {fake_jwt}"})
        test_results.append({"test": "JWT Alg 'none' bypass", "status": r11.status_code, "body": r11.text[:200]})

        # Test 12: Invalid Query Parameter Types (limit='abc', offset=-50)
        print("[*] Test 12: Malformed pagination params (limit=abc, offset=-50)")
        r12 = await client.get(f"{BASE_URL}/expenses?limit=abc&offset=-50", headers=headers)
        test_results.append({"test": "Malformed pagination parameters", "status": r12.status_code, "body": r12.text[:200]})

        # Test 13: Limit Overflow (limit=9999999)
        print("[*] Test 13: Limit overflow (limit=9999999)")
        r13 = await client.get(f"{BASE_URL}/expenses?limit=9999999", headers=headers)
        test_results.append({"test": "Limit overflow (limit=9999999)", "status": r13.status_code, "body": r13.text[:200]})

        # Test 14: Race Condition: 50 Concurrent DELETEs of the same transaction ID
        print("[*] Test 14: Race condition: 50 concurrent DELETEs of identical tx_id")
        # First create a transaction to delete
        create_res = await client.post(f"{BASE_URL}/expenses", json={"type": "expense", "amount": 99.99, "comment": "To be deleted"}, headers=headers)
        target_tx_id = create_res.json()["id"]
        
        delete_statuses = []
        async def do_delete():
            try:
                res = await client.delete(f"{BASE_URL}/expenses/{target_tx_id}", headers=headers)
                delete_statuses.append(res.status_code)
            except Exception as e:
                delete_statuses.append(str(e))

        await asyncio.gather(*[do_delete() for _ in range(50)])
        test_results.append({
            "test": "Concurrent 50x DELETE on same tx_id",
            "status": "Aggregated",
            "body": f"Statuses count: { {s: delete_statuses.count(s) for s in set(delete_statuses)} }"
        })

    with open("coolify_negative_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)

    print("\n=== SUMMARY OF NEGATIVE & FUZZING TESTS ===")
    for t in test_results:
        print(f"[{t['status']}] {t['test']} -> {t['body'][:80]}")

if __name__ == "__main__":
    asyncio.run(run_negative_tests())
