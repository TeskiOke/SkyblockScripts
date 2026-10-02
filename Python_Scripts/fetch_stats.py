import requests

def fetch_stats(username):
    url = f"https://sky.shiiyu.moe/stats/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            # Look for specific markers in the HTML
            # Networth, Levels, etc are usually in meta tags or script objects
            content = response.text
            with open("stats.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("Successfully saved stats.html")
        else:
            print(f"Failed to fetch: {response.reason}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_stats("TeskiOke")
