import time
import requests
import threading
from flask import Flask, request, render_template

# App create
app = Flask(__name__)

# URL List
monitored_urls = []

# --- BACKGROUND MONITOR ---
def monitor_background_task():
    while True:
        if monitored_urls:
            print(f"\n[Monitor] Checking {len(monitored_urls)} URLs...")
            for url in monitored_urls:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Monitor Bot)'}
                    requests.get(url, headers=headers, timeout=10)
                    print(f"✅ Pinged: {url}")
                except Exception as e:
                    print(f"❌ Error: {url} | {e}")
        time.sleep(60)

# Thread Start
threading.Thread(target=monitor_background_task, daemon=True).start()

# --- ROUTES ---

@app.route('/')
def home():
    # Ab ye 'templates/index.html' file ko dhundega
    return render_template('index.html', urls=monitored_urls)

@app.route('/add', methods=['POST'])
def add_url():
    url = request.form.get('url')
    if url and url.startswith('http'):
        if url not in monitored_urls:
            monitored_urls.append(url)
    return home()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
