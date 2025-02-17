import os
import telebot
import requests
import openai
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===== إعدادات البوت =====
TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not TOKEN:
    raise ValueError("🚨 خطأ: لم يتم العثور على توكن البوت! تأكد من ضبط المتغير البيئي BOT_TOKEN في Render.")
bot = telebot.TeleBot(TOKEN)

# ===== مفاتيح API =====
DEEPAI_API_KEY = os.getenv("DEEPAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# ===== أيدي المطور =====
DEVELOPER_ID = 7601607055  # ضع أيدي المطور هنا
DEVELOPER_USERNAME = "A7-pro"  # ضع اسم المستخدم للمطور

# ===== تحليل النصوص باستخدام OpenAI =====
def analyze_text_with_openai(text):
    prompt = f"""
    النص التالي قد يحتوي على إساءة أو قذف. قم بتحليل النص وأخبرني إذا كان يحتوي على لغة غير لائقة:
    النص: "{text}"
    هل يحتوي النص على إساءة؟ الإجابة نعم أو لا.
    """
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "تحليل النصوص"}, {"role": "user", "content": prompt}],
            max_tokens=5,
            temperature=0
        )
        result = response.choices[0].message['content'].strip().lower()
        return "نعم" in result
    except Exception as e:
        print(f"خطأ أثناء تحليل النصوص: {e}")
        return False

# ===== تحليل الصور باستخدام DeepAI =====
def analyze_image_with_deepai(file_path):
    try:
        url = "https://api.deepai.org/api/nsfw-detector"
        with open(file_path, 'rb') as image:
            response = requests.post(
                url,
                files={'image': image},
                headers={'api-key': DEEPAI_API_KEY}
            )
        result = response.json()
        return result.get('output', {}).get('nsfw_score', 0) > 0.5
    except Exception as e:
        print(f"خطأ أثناء تحليل الصورة: {e}")
        return False

# ===== إرسال تقرير للمطور =====
def notify_developer(message, content_type, details):
    try:
        bot.send_message(
            DEVELOPER_ID,
            f"🚨 **اكتشاف محتوى مشبوه**\n"
            f"📩 النوع: {content_type}\n"
            f"👤 المرسل: @{message.from_user.username} (ID: {message.from_user.id})\n"
            f"📍 المجموعة: {message.chat.title}\n"
            f"🔍 التفاصيل: {details}",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"خطأ أثناء إرسال التقرير للمطور: {e}")

# ===== استقبال الأوامر (ترحيب عند /start) =====
@bot.message_handler(commands=['start'])
def welcome_message(message):
    markup = InlineKeyboardMarkup()
    add_bot_button = InlineKeyboardButton("➕ أضف البوت إلى مجموعتك", url=f"https://t.me/{bot.get_me().username}?startgroup=true")
    markup.add(add_bot_button)
    
    bot.send_message(
        message.chat.id,
        f"👋 أهلاً وسهلاً بك! هذا البوت يمنع السب والصور غير اللائقة. 🚫\n\n👨‍💻 المطور: @{DEVELOPER_USERNAME}",
        reply_markup=markup
    )

# ===== استقبال النصوص ومنع السب =====
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.chat.type != "private" and analyze_text_with_openai(message.text):
        bot.delete_message(message.chat.id, message.message_id)
        notify_developer(message, "نص", message.text)

# ===== استقبال الصور ومنع الصور غير اللائقة =====
@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_path = f"./{file_info.file_path.split('/')[-1]}"
        
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        if analyze_image_with_deepai(file_path):
            bot.delete_message(message.chat.id, message.message_id)
            notify_developer(message, "صورة", "🚫 الصورة تحتوي على محتوى غير لائق.")
    except Exception as e:
        print(f"خطأ أثناء استقبال الصورة: {e}")

# ===== تشغيل البوت =====
print("🚀 البوت يعمل الآن...")
bot.infinity_polling()

