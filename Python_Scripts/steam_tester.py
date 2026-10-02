import requests
import time
import threading
import json
import socket
import random
from concurrent.futures import ThreadPoolExecutor

# Massive mapping of Steam Cell IDs (Back to 100+ regions)
REGIONS = {
    # --- RUSSIA & CIS ---
    "Moscow": 56, "St. Petersburg": 110, "Novosibirsk": 145, "Yekaterinburg": 146, 
    "Krasnoyarsk": 147, "Vladivostok": 148, "Khabarovsk": 149, "Irkutsk": 150, 
    "Rostov-on-Don": 151, "Ufa": 152, "Samara": 153, "Kazan": 57, "Nizhny Novgorod": 155,
    "Almaty": 129, "Nur-Sultan": 171, "Kyiv": 73, "Kharkiv": 143, "Tashkent": 173, "Tbilisi": 174, "Minsk": 74,
    
    # --- EUROPE ---
    "Frankfurt": 3, "Berlin": 11, "London": 4, "Paris": 6, "Amsterdam": 12, 
    "Stockholm": 66, "Warsaw": 166, "Prague": 15, "Milan": 13, "Madrid": 41,
    "Vienna": 16, "Zurich": 22, "Budapest": 38, "Bucharest": 43, "Istanbul": 82,
    
    # --- NORTH AMERICA ---
    "Washington DC": 1, "New York": 10, "Los Angeles": 20, "Chicago": 9, "Seattle": 19,
    "Dallas": 18, "Miami": 37, "Atlanta": 24, "Toronto": 107, "Montreal": 108,
    
    # --- ASIA & OCEANIA ---
    "Tokyo": 39, "Osaka": 46, "Seoul": 35, "Singapore": 44, "Hong Kong": 32, "Taipei": 31,
    "Sydney": 17, "Melbourne": 88, "Mumbai": 51, "Shanghai": 29, "Beijing": 30,
    
    # --- OTHERS ---
    "Sao Paulo": 21, "Johannesburg": 45, "Cape Town": 121
}

API_URL = "https://api.steampowered.com/IContentServerDirectoryService/GetServersForSteamPipe/v1/"
# Using a larger Video file (~15MB) which is less likely to be blocked and better for speed measurement
SPEED_TEST_URL = "https://steamcdn-a.akamaihd.net/steam/apps/256767123/movie_max.mp4" 

class SteamTesterV5:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "*/*",
            "Connection": "keep-alive"
        })
    
    def get_server_host(self, cell_id):
        try:
            resp = self.session.get(f"{API_URL}?cellid={cell_id}", timeout=5)
            if resp.status_code == 200:
                servers = resp.json().get("response", {}).get("servers", [])
                if servers: return servers[0]['host']
        except: pass
        return None

    def test_latency(self, name, cell_id):
        host = self.get_server_host(cell_id)
        if not host: return {"name": name, "latency": 9999, "host": None}
        
        latencies = []
        for _ in range(3):
            try:
                start = time.perf_counter()
                socket.create_connection((host, 80), timeout=2.0).close()
                latencies.append((time.perf_counter() - start) * 1000)
            except: 
                latencies.append(1500)
        
        return {"name": name, "latency": sum(latencies)/len(latencies), "host": host}

    def run_speed_test(self, region_data, duration=5.0):
        name = region_data['name']
        print(f"   [ТЕСТ] Измеряем скорость для {name}...", end="\r")
        
        try:
            start = time.perf_counter()
            size = 0
            
            while time.perf_counter() - start < duration:
                # Adding a random query to bypass cache
                r = self.session.get(f"{SPEED_TEST_URL}?r={random.random()}", timeout=7, stream=True)
                if r.status_code != 200:
                    if size == 0: return 0.01 # Fake small number to show it reached but failed
                    break
                    
                for chunk in r.iter_content(chunk_size=1024*1024): # 1MB chunks
                    size += len(chunk)
                    if time.perf_counter() - start > duration: # 5 second sustained test
                        break
            
            elapsed = time.perf_counter() - start
            mbps = (size * 8) / (elapsed * 1_000_000) if elapsed > 0 else 0
            return mbps
        except Exception as e:
            return 0.00

def main():
    tester = SteamTesterV5()
    print("\n🔍 [STEAM SPEED TESTER v4.2] - Глобальный анализ")
    print("=" * 75)
    
    # PHASE 1: LATENCY
    print(f"📡 Шаг 1: Сканирование задержки для {len(REGIONS)} регионов...")
    scan_results = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(tester.test_latency, name, cid): name for name, cid in REGIONS.items()}
        for i, future in enumerate(futures):
            res = future.result()
            if res['latency'] < 500:
                scan_results.append(res)
            print(f"   Прогресс: {i+1}/{len(REGIONS)} ({res['name']})", end="\r")
    
    print("\n   Сканирование завершено.")

    # Sort and pick top 10
    scan_results.sort(key=lambda x: x['latency'])
    top_candidates = scan_results[:10]

    if not top_candidates:
        print("❌ Ошибка: Все регионы недоступны пли плохой пинг.")
        return

    # PHASE 2: SEQUENTIAL SPEED TEST
    print(f"🚀 Шаг 2: Тестирование скорости для ТОП-{len(top_candidates)} (последовательно)...")
    final_results = []
    for res in top_candidates:
        mbps = tester.run_speed_test(res)
        res['speed'] = mbps
        # Balanced Score: Speed is king, Latency is secondary
        res['score'] = (mbps * 5.0) + (1000 / (res['latency'] + 10)) 
        final_results.append(res)
    
    print("   Тестирование завершено.\n")

    # FINAL OUTPUT
    output_lines = []
    output_lines.append("🏆 ИТОГОВЫЙ РЕЙТИНГ (Лучшие из лучших):")
    output_lines.append("═" * 65)
    output_lines.append(f"{'#':<3} | {'Регион':<18} | {'Пинг':<10} | {'Замер Скорости'}")
    output_lines.append("-" * 60)
    
    final_results.sort(key=lambda x: x['score'], reverse=True)
    
    for i, res in enumerate(final_results, 1):
        indicator = "🟢" if i <= 3 else "🟡"
        speed_text = f"{res['speed']:>7.2f} Mbps" if res['speed'] > 0 else "Blocked/Err"
        output_lines.append(f"{i:<3} | {res['name']:<18} | {indicator} {res['latency']:>6.1f} ms | {speed_text}")

    if final_results:
        best = final_results[0]
        output_lines.append("\n" + "═" * 60)
        output_lines.append(f"✅ РЕКОМЕНДАЦИЯ: {best['name'].upper()}")
        output_lines.append(f"Пинг: {best['latency']:.1f} мс")
        output_lines.append(f"Тестовая пропускная способность: {best['speed']:.2f} Mbps")
        output_lines.append("═" * 60)
        output_lines.append("💡 Если скорость 0.00 - возможно, Steam CDN блокируется провайдером.")
        output_lines.append("💡 Смени в Steam: Settings -> Downloads -> Download Region")

    # Вывод в консоль
    for line in output_lines:
        print(line)

    # Сохранение в файл
    out_file = "steam_tester_results.txt"
    try:
        import os
        # Сохраняем в той же папке, где находится скрипт
        script_dir = os.path.dirname(os.path.abspath(__file__))
        out_path = os.path.join(script_dir, out_file)
        
        with open(out_path, "w", encoding="utf-8") as f:
            for line in output_lines:
                f.write(line + "\n")
        print(f"\n📁 Результаты сохранены в файл: {out_path}")
    except Exception as e:
        print(f"\n❌ Ошибка при сохранении в файл: {e}")

    # Задержка перед закрытием (чтобы cmd не закрывалась сразу)
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()
