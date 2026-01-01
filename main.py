import time
import requests
import threading
from flask import Flask, request, render_template_string

# Flask App create kar rahe hain
app = Flask(__name__)

# Yahan hum saare URLs store karenge (Database ki jagah abhi List use kar rahe hain)
monitored_urls = []

# --- BACKGROUND MONITOR SYSTEM ---
def monitor_background_task():
    """
    Ye function background mein chalta rahega.
    Ye har 60 seconds (1 minute) mein saare saved URLs ko ping karega.
    """
    while True:
        if monitored_urls:
            print(f"\n[Monitor] Checking {len(monitored_urls)} URLs...")
            for url in monitored_urls:
                try:
                    # Fake User-Agent taaki server ko lage koi real insaan hai
                    headers = {'User-Agent': 'Mozilla/5.0 (Monitor Bot)'}
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        print(f"✅ Success: {url} is Active")
                    else:
                        print(f"⚠️ Warning: {url} returned {response.status_code}")
                except Exception as e:
                    print(f"❌ Error pinging {url}: {e}")
        else:
            print("[Monitor] No URLs to monitor yet. Waiting...")

        # 1 Minute (60 Seconds) ka wait
        time.sleep(60)

# Threading start karna (Taaki website aur monitor saath mein chalein)
threading.Thread(target=monitor_background_task, daemon=True).start()


# --- FRONTEND (HTML CODE) ---
# Ye simple HTML page hai jo user ko dikhega
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>My Personal Monitor</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding: 50px; background-color: #f4f4f9; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); max-width: 500px; margin: auto; }
        input[type="text"] { width: 80%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #218838; }
        ul { list-style: none; padding: 0; }
        li { background: #e9ecef; margin: 5px 0; padding: 10px; border-radius: 5px; text-align: left; word-break: break-all; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🚀 Bot Uptime Monitor</h2>
        <p>Apna Bot ya Website URL niche daalein. <br>Hum ise har <b>1 Minute</b> mein ping karenge.</p>
        
        <form action="/add" method="POST">
            <input type="text" name="url" placeholder="https://your-bot-url.com" required>
            <br>
            <button type="submit">Start Monitoring</button>
        </form>

        <h3>Currently Monitoring:</h3>
        <ul>
            {% for url in urls %}
                <li>🟢 {{ url }}</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

# --- WEBSERVER ROUTES ---

@app.route('/')
def home():
    # Home page par form aur list dikhaye
    return render_template_string(HTML_PAGE, urls=monitored_urls)

@app.route('/add', methods=['POST'])
def add_url():
    # Form se URL lena
    url = request.form.get('url')
    
    # Check karna ki URL valid hai ya nahi
    if url and url.startswith('http'):
        if url not in monitored_urls:
            monitored_urls.append(url)
    
    return home() # Wapas home page par bhej do

# App Run karna
if __name__ == "__main__":
    # Port 5000 par chalega
    app.run(host='0.0.0.0', port=5000)
