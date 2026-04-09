import os
import anthropic
import requests
import psycopg2
from datetime import datetime
import schedule
import time
from flask import Flask, jsonify

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_IDS = os.environ.get("CHAT_IDS", "").split(",")
DATABASE_URL = os.environ.get("DATABASE_URL")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

BRAND = "7bees"
PRODUCTS = "Dhofar frankincense honey, Samr honey, Sidr honey, African luxury honey, Gorillas Coffee, Rwanda Mountain Tea"
AUDIENCE = "All segments age 18-80, UAE residents, value quality and authenticity"
STYLE = "Luxury, warm, trustworthy, Gulf Arabic"
RULES = "No repetition, every post has value, respect UAE occasions"

def get_db():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS marketing_content (
            id SERIAL PRIMARY KEY,
            platform VARCHAR(50),
            content TEXT,
            content_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW(),
            published BOOLEAN DEFAULT FALSE
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def save_content(platform, content, content_type):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO marketing_content (platform, content, content_type) VALUES (%s, %s, %s)",
        (platform, content, content_type)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_recent_topics():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT content FROM marketing_content ORDER BY created_at DESC LIMIT 10")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [r[0][:100] for r in rows]
    except:
        return []

def generate_daily_content():
    recent = get_recent_topics()
    recent_text = "\n".join(recent) if recent else "No previous content"

    prompt = f"""You are a luxury marketing manager for {BRAND} in UAE.
Products: {PRODUCTS}
Audience: {AUDIENCE}
Style: {STYLE}
Rules: {RULES}

Recent topics to avoid:
{recent_text}

Generate daily social media content in Arabic (Gulf dialect, warm and luxurious tone):

---INSTAGRAM_1---
Caption (3-4 lines about health benefit):
Hashtags (15 tags):
Best posting time:
Photo idea:
---END---

---INSTAGRAM_2---
Caption (3-4 lines about honey origin story):
Hashtags (15 tags):
Best posting time:
Photo idea:
---END---

---INSTAGRAM_3---
Caption (3-4 lines recipe or usage tip):
Hashtags (15 tags):
Best posting time:
Photo idea:
---END---

---TIKTOK_1---
Title:
Script (30-60 seconds):
Suggested music:
Hashtags:
---END---

---TIKTOK_2---
Title:
Script:
Suggested music:
Hashtags:
---END---

---SNAPCHAT---
Text (1-2 lines):
Suggested filter:
---END---
"""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def generate_weekly_analysis():
    prompt = f"""You are a luxury marketing manager for {BRAND} in UAE.
Products: {PRODUCTS}

Write a weekly market analysis report in Arabic including:
1. Top honey
cat > marketing_agent.py << 'PYEOF'
import os
import anthropic
import requests
import psycopg2
from datetime import datetime
import schedule
import time
from flask import Flask, jsonify

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_IDS = os.environ.get("CHAT_IDS", "").split(",")
DATABASE_URL = os.environ.get("DATABASE_URL")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

BRAND = "7bees"
PRODUCTS = "Dhofar frankincense honey, Samr honey, Sidr honey, African luxury honey, Gorillas Coffee, Rwanda Mountain Tea"
AUDIENCE = "All segments age 18-80, UAE residents, value quality and authenticity"
STYLE = "Luxury, warm, trustworthy, Gulf Arabic"
RULES = "No repetition, every post has value, respect UAE occasions"

def get_db():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS marketing_content (
            id SERIAL PRIMARY KEY,
            platform VARCHAR(50),
            content TEXT,
            content_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW(),
            published BOOLEAN DEFAULT FALSE
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def save_content(platform, content, content_type):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO marketing_content (platform, content, content_type) VALUES (%s, %s, %s)",
        (platform, content, content_type)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_recent_topics():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT content FROM marketing_content ORDER BY created_at DESC LIMIT 10")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [r[0][:100] for r in rows]
    except:
        return []

def generate_daily_content():
    recent = get_recent_topics()
    recent_text = "\n".join(recent) if recent else "No previous content"

    prompt = f"""You are a luxury marketing manager for {BRAND} in UAE.
Products: {PRODUCTS}
Audience: {AUDIENCE}
Style: {STYLE}
Rules: {RULES}

Recent topics to avoid:
{recent_text}

Generate daily social media content in Arabic (Gulf dialect, warm and luxurious tone):

---INSTAGRAM_1---
Caption (3-4 lines about health benefit):
Hashtags (15 tags):
Best posting time:
Photo idea:
---END---

---INSTAGRAM_2---
Caption (3-4 lines about honey origin story):
Hashtags (15 tags):
Best posting time:
Photo idea:
---END---

---INSTAGRAM_3---
Caption (3-4 lines recipe or usage tip):
Hashtags (15 tags):
Best posting time:
Photo idea:
---END---

---TIKTOK_1---
Title:
Script (30-60 seconds):
Suggested music:
Hashtags:
---END---

---TIKTOK_2---
Title:
Script:
Suggested music:
Hashtags:
---END---

---SNAPCHAT---
Text (1-2 lines):
Suggested filter:
---END---
"""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def generate_weekly_analysis():
    prompt = f"""You are a luxury marketing manager for {BRAND} in UAE.
Products: {PRODUCTS}

Write a weekly market analysis report in Arabic including:
1. Top honey and natural products competitors in UAE social media
2. Most engaging content types in this category
3. Untapped opportunities for 7bees
4. Strategic recommendation for next week
5. Top 3 content ideas inspired by market trends

Write as a concise executive report in Arabic.
"""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def send_telegram(message, chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data, timeout=30)
    except Exception as e:
        print(f"Telegram error: {e}")

def send_to_all(message):
    for chat_id in CHAT_IDS:
        chat_id = chat_id.strip()
        if chat_id:
            if len(message) > 4000:
                parts = [message[i:i+4000] for i in range(0, len(message), 4000)]
                for part in parts:
                    send_telegram(part, chat_id)
            else:
                send_telegram(message, chat_id)

def daily_job():
    print(f"[{datetime.now()}] Generating daily content...")
    try:
        content = generate_daily_content()
        save_content("all", content, "daily")
        date_str = datetime.now().strftime("%Y-%m-%d")
        send_to_all(f"*7bees Daily Content - {date_str}*\n\n{content}")
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
        send_to_all(f"Error generating content: {e}")

def weekly_job():
    print(f"[{datetime.now()}] Generating weekly report...")
    try:
        analysis = generate_weekly_analysis()
        send_to_all(f"*7bees Weekly Report*\n\n{analysis}")
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "7bees Marketing Agent is running"})

@app.route("/generate-now")
def generate_now():
    daily_job()
    return jsonify({"status": "Content generated and sent"})

@app.route("/weekly-now")
def weekly_now():
    weekly_job()
    return jsonify({"status": "Weekly report sent"})

def run_scheduler():
    schedule.every().day.at("04:00").do(daily_job)
    schedule.every().sunday.at("05:00").do(weekly_job)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    init_db()
    print("7bees Marketing Agent starting...")
    import threading
    t = threading.Thread(target=run_scheduler, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
