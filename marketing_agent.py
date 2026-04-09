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

def get_db():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    sql = """CREATE TABLE IF NOT EXISTS marketing_content (
        id SERIAL PRIMARY KEY,
        platform VARCHAR(50),
        content TEXT,
        content_type VARCHAR(50),
        created_at TIMESTAMP DEFAULT NOW(),
        published BOOLEAN DEFAULT FALSE
    )"""
    cur.execute(sql)
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
    except Exception:
        return []

def generate_daily_content():
    recent = get_recent_topics()
    recent_text = chr(10).join(recent) if recent else "No previous content"
    prompt = (
        "You are a luxury marketing manager for 7bees in UAE.\n"
        "Products: Dhofar frankincense honey, Samr honey, Sidr honey, African luxury honey, Gorillas Coffee, Rwanda Mountain Tea\n"
        "Audience: All segments age 18-80, UAE residents, value quality\n"
        "Style: Luxury, warm, Gulf Arabic\n"
        "Recent topics to avoid:\n" + recent_text + "\n\n"
        "Generate daily social media content in Arabic:\n\n"
        "---INSTAGRAM_1---\n"
        "Caption (3-4 lines health benefit):\n"
        "Hashtags (15 tags):\n"
        "Best posting time:\n"
        "Photo idea:\n"
        "---END---\n\n"
        "---INSTAGRAM_2---\n"
        "Caption (3-4 lines honey origin):\n"
        "Hashtags (15 tags):\n"
        "Best posting time:\n"
        "Photo idea:\n"
        "---END---\n\n"
        "---INSTAGRAM_3---\n"
        "Caption (3-4 lines recipe or tip):\n"
        "Hashtags (15 tags):\n"
        "Best posting time:\n"
        "Photo idea:\n"
        "---END---\n\n"
        "---TIKTOK_1---\n"
        "Title:\nScript (30-60 sec):\nMusic:\nHashtags:\n"
        "---END---\n\n"
        "---TIKTOK_2---\n"
        "Title:\nScript:\nMusic:\nHashtags:\n"
        "---END---\n\n"
        "---SNAPCHAT---\n"
        "Text (1-2 lines):\nFilter:\n"
        "---END---"
    )
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def generate_weekly_analysis():
    prompt = (
        "You are a luxury marketing manager for 7bees in UAE.\n"
        "Write a weekly market analysis in Arabic including:\n"
        "1. Top honey competitors in UAE social media\n"
        "2. Most engaging content types\n"
        "3. Untapped opportunities for 7bees\n"
        "4. Strategic recommendation for next week\n"
        "5. Top 3 content ideas from market trends"
    )
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def send_telegram(message, chat_id):
    url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data, timeout=30)
    except Exception as e:
        print("Telegram error: " + str(e))

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
    print("Generating daily content...")
    try:
        content = generate_daily_content()
        save_content("all", content, "daily")
        date_str = datetime.now().strftime("%Y-%m-%d")
        send_to_all("*7bees Daily Content - " + date_str + "*\n\n" + content)
        print("Done!")
    except Exception as e:
        print("Error: " + str(e))
        send_to_all("Error: " + str(e))

def weekly_job():
    print("Generating weekly report...")
    try:
        analysis = generate_weekly_analysis()
        send_to_all("*7bees Weekly Report*\n\n" + analysis)
        print("Done!")
    except Exception as e:
        print("Error: " + str(e))

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
