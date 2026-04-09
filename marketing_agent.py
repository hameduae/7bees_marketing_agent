import os
import anthropic
import requests
import psycopg2
from datetime import datetime
import schedule
import time

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN    = os.environ.get("TELEGRAM_TOKEN")
CHAT_IDS          = os.environ.get("CHAT_IDS", "").split(",")
DATABASE_URL      = os.environ.get("DATABASE_URL")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

AGENT_SKILL = """
أنت "نحلة" — مدير التسويق الرقمي لعلامة 7bees الفاخرة في الإمارات.
المنتجات: عسل اللبان الظفاري، عسل السمر، عسل السدر، العسل الإفريقي الفاخر، قهوة Gorillas، شاي Rwanda.
الجمهور: 18-80 سنة، جميع فئات المجتمع، يقدّرون الجودة والأصالة.
الأسلوب: فاخر، دافئ، موثوق، عربي فصيح خل
cat > ~/Desktop/7bees_marketing_agent/marketing_agent.py << 'ENDOFFILE'
import os
import anthropic
import requests
import psycopg2
from datetime import datetime
import schedule
import time

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN    = os.environ.get("TELEGRAM_TOKEN")
CHAT_IDS          = os.environ.get("CHAT_IDS", "").split(",")
DATABASE_URL      = os.environ.get("DATABASE_URL")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

AGENT_SKILL = """
أنت "نحلة" — مدير التسويق الرقمي لعلامة 7bees الفاخرة في الإمارات.
المنتجات: عسل اللبان الظفاري، عسل السمر، عسل السدر، العسل الإفريقي الفاخر، قهوة Gorillas، شاي Rwanda.
الجمهور: 18-80 سنة، جميع فئات المجتمع، يقدّرون الجودة والأصالة.
الأسلوب: فاخر، دافئ، موثوق، عربي فصيح خليجي.
القواعد: لا تكرار، كل بوست يحمل قيمة، راعِ المناسبات الإماراتية.
"""

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
    recent_text = "\n".join(recent) if recent else "لا يوجد محتوى سابق"
    prompt = f"""
{AGENT_SKILL}

المواضيع الأخيرة (تجنّبها):
{recent_text}

أنشئ المحتوى التالي:

---INSTAGRAM_1---
الكابشن (3-4 أسطر عن فائدة صحية):
الهاشتاقات (15 هاشتاق):
أفضل وقت النشر:
فكرة الصورة:
---END---

---INSTAGRAM_2---
الكابشن (3-4 أسطر عن قصة مصدر العسل):
الهاشتاقات (15 هاشتاق):
أفضل وقت النشر:
فكرة الصورة:
---END---

---INSTAGRAM_3---
الكابشن (3-4 أسطر وصفة أو طريقة استخدام):
الهاشتاقات (15 هاشتاق):
أفضل وقت النشر:
فكرة الصورة:
---END---

---TIKTOK_1---
العنوان:
السكريبت (30-60 ثانية):
الموسيقى المقترحة:
الهاشتاقات:
---END---

---TIKTOK_2---
العنوان:
السكريبت:
الموسيقى المقترحة:
الهاشتاقات:
---END---

---SNAPCHAT---
النص (سطر أو سطران):
الفلتر المقترح:
---END---
"""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def generate_weekly_analysis():
    prompt = f"""
{AGENT_SKILL}

قدّم تقرير أسبوعي يتضمن:
1. أبرز منافسي العسل في UAE على السوشيال ميديا
2. أكثر أنواع المحتوى تفاعلاً في هذا المجال
3. فرص غير مستغلة لـ 7bees
4. توصية استراتيجية للأسبوع القادم
5. أفضل 3 أفكار محتوى مستوحاة من السوق

اكتب بأسلوب تقرير تنفيذي مختصر باللغة العربية.
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
        print(f"خطأ تيليغرام: {e}")

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
    print(f"[{datetime.now()}] توليد المحتوى اليومي...")
    try:
        content = generate_daily_content()
        save_content("all", content, "daily")
        date_str = datetime.now().strftime("%Y-%m-%d")
        send_to_all(f"🍯 *محتوى 7bees — {date_str}*\n\n{content}")
        print("تم الارسال")
    except Exception as e:
        print(f"خطأ: {e}")
        send_to_all(f"خطأ في توليد المحتوى: {e}")

def weekly_job():
    print(f"[{datetime.now()}] التقرير الأسبوعي...")
    try:
        analysis = generate_weekly_analysis()
        send_to_all(f"📊 *تقرير 7bees الأسبوعي*\n\n{analysis}")
        print("تم الارسال")
    except Exception as e:
        print(f"خطأ: {e}")

from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "7bees Marketing Agent يعمل"})

@app.route("/generate-now")
def generate_now():
    daily_job()
    return jsonify({"status": "تم توليد المحتوى"})

@app.route("/weekly-now")
def weekly_now():
    weekly_job()
    return jsonify({"status": "تم إرسال التقرير"})

def run_scheduler():
    schedule.every().day.at("04:00").do(daily_job)
    schedule.every().sunday.at("05:00").do(weekly_job)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    init_db()
    print("7bees Marketing Agent يعمل")
    import threading
    t = threading.Thread(target=run_scheduler, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
