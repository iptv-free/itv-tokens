import requests
import time
import os
import sys

# === SOZLAMALAR ===
WORKER_URL = os.environ.get("WORKER_URL", "").strip().rstrip("/")
SECRET_KEY = os.environ.get("SECRET_KEY", "").strip()
CHANNEL_RANGE = range(1, 301)
OUTPUT_M3U = "itv_channels.m3u"
# ==================

# Tekshirish
if not WORKER_URL:
    print("XATO: WORKER_URL sozlanmagan!")
    print("GitHub Secrets da WORKER_URL = https://itvuz.playtv2099.workers.dev bo'lishi kerak")
    sys.exit(1)

if not SECRET_KEY:
    print("XATO: SECRET_KEY sozlanmagan!")
    sys.exit(1)

print(f"Worker URL: {WORKER_URL}")
print(f"Secret key: {'*' * len(SECRET_KEY)}")

API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://itv.uz/",
    "Origin": "https://itv.uz",
    "Accept": "application/json",
}

def fetch_all_channels():
    channels = []
    print("\nKanallar skanlanmoqda...\n")
    for ch_id in CHANNEL_RANGE:
        try:
            url = f"https://api.itv.uz/v2/cards/channels/show?channelId={ch_id}"
            r = requests.get(url, headers=API_HEADERS, timeout=5)
            if r.status_code != 200:
                continue
            data = r.json()
            if not data.get("data"):
                continue
            ch_data = data["data"]
            stream_url = ch_data.get("files", {}).get("streamUrl", "")
            name = ch_data.get("channelTitle", f"Kanal {ch_id}")
            logo = ch_data.get("files", {}).get("posterUrl", "")
            if not stream_url:
                continue
            channels.append({"id": ch_id, "name": name, "logo": logo, "stream_url": stream_url})
            print(f"  ✓ [{ch_id:03d}] {name}")
        except Exception as e:
            print(f"  ✗ [{ch_id:03d}] {e}")
        time.sleep(0.1)
    return channels

def save_m3u(channels):
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write('#EXTM3U x-tvg-url=""\n\n')
        for ch in channels:
            f.write(f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}" tvg-logo="{ch["logo"]}" group-title="ITV.uz",{ch["name"]}\n')
            f.write(f'{WORKER_URL}/channel/{ch["id"]}.m3u8\n\n')
    print(f"\n✅ M3U fayl saqlandi: {OUTPUT_M3U} ({len(channels)} kanal)")

def push_tokens(channels):
    tokens = {
        str(ch["id"]): {"url": ch["stream_url"], "name": ch["name"], "logo": ch["logo"]}
        for ch in channels
    }
    push_url = f"{WORKER_URL}/update-tokens"
    print(f"\nPush qilinmoqda: {push_url}")
    r = requests.post(
        push_url,
        json=tokens,
        headers={"x-secret": SECRET_KEY, "Content-Type": "application/json"},
        timeout=30
    )
    print(f"Worker javob: {r.status_code} - {r.json()}")

def main():
    print("=" * 40)
    print("  ITV Token Pusher (GitHub Actions)")
    print("=" * 40)
    channels = fetch_all_channels()
    print(f"\nTopildi: {len(channels)} ta kanal")
    save_m3u(channels)
    push_tokens(channels)
    print("\n✅ Tayyor!")

if __name__ == "__main__":
    main()
