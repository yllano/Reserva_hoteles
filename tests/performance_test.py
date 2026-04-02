import requests
import time
import concurrent.futures
import statistics

BASE_URL = "http://localhost:8000/api/hotels"

def make_request():
    try:
        start = time.time()
        response = requests.get(BASE_URL, timeout=5)
        end = time.time()
        return response.status_code, end - start
    except Exception as e:
        return "ERROR", 0

def run_test(name, concurrency, total_requests):
    print(f"--- Running {name} ({concurrency} concurrent users, {total_requests} total requests) ---")
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(make_request) for _ in range(total_requests)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            
    status_codes = [r[0] for r in results]
    latencies = [r[1] for r in results if r[0] != "ERROR"]
    
    success_count = status_codes.count(200)
    error_count = len(status_codes) - success_count
    
    print(f"Success: {success_count}, Errors: {error_count}")
    if latencies:
        print(f"Average Latency: {statistics.mean(latencies):.4f}s")
        print(f"Min Latency: {min(latencies):.4f}s")
        print(f"Max Latency: {max(latencies):.4f}s")
    print("-" * 50)
    return {
        "name": name,
        "concurrency": concurrency,
        "success": success_count,
        "errors": error_count,
        "avg_latency": statistics.mean(latencies) if latencies else 0
    }

if __name__ == "__main__":
    # Capacity Test (Light Load)
    run_test("Capacity Test", 5, 20)
    
    # Load Test (Moderate)
    run_test("Load Test", 20, 50)
    
    # Stress Test (Heavy)
    run_test("Stress Test", 30, 50)
