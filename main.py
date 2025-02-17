# تحديث الكود ليشمل الترحيب عند /start ومنع السب ومنع الصور
bot_code_updated = """\
import telebot
import requests
import openai

# ===== إعدادات البوت =====
TOKEN = "ضع_توكن_البوت_هنا"  # توكن البوت من BotFather
bot = telebot.TeleBot(TOKEN)

# ===== مفاتيح API =====
DEEPAI_API_KEY = "ضع_مفتاح_DeepAI_هنا"  # مفتاح DeepAI لتحليل الصور
OPENAI_API_KEY = "ضع_مفتاح_OpenAI_هنا"  # مفتاح OpenAI لتحليل النصوص
openai.api_key = OPENAI_API_KEY

# ===== أيدي المطور =====
DEVELOPER_ID = 7601607055  # ضع أيدي المطور هنا

# ===== تحليل النصوص باستخدام OpenAI =====
def analyze_text_with_openai(text):
    prompt = f\"\"\"
    النص التالي قد يحتوي على إساءة أو قذف. قم بتحليل النص وأخبرني إذا كان يحتوي على لغة غير لائقة:
    النص: "{text}"
    هل يحتوي النص على إساءة؟ الإجابة نعم أو لا.
    \"\"\"
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=5,
            temperature=0
        )
        result = response.choices[0].text.strip().lower()
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
        nsfw_score = result.get('output', {}).get('nsfw_score', 0)
        return nsfw_score > 0.5  # إذا كانت النتيجة أعلى من 0.5، اعتبرها غير لائقة
    except Exception as e:
        print(f"خطأ أثناء تحليل الصورة: {e}")
        return False

# ===== إرسال تقرير للمطور =====
def notify_developer(message, content_type, details):
    try:
        bot.send_message(
            DEVELOPER_ID,
            f"🚨 **اكتشاف محتوى مشبوه**\\n"
            f"📩 النوع: {content_type}\\n"
            f"👤 المرسل: @{message.from_user.username} (ID: {message.from_user.id})\\n"
            f"📍 المجموعة: {message.chat.title}\\n"
            f"🔍 التفاصيل: {details}",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"خطأ أثناء إرسال التقرير للمطور: {e}")

# ===== استقبال الأوامر (ترحيب عند /start) =====
@bot.message_handler(commands=['start'])
def welcome_message(message):
    bot.reply_to(message, "👋 أهلاً وسهلاً بك! هذا البوت يمنع السب والصور غير اللائقة. 🚫")

# ===== استقبال النصوص ومنع السب =====
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.chat.type != "private":
        if analyze_text_with_openai(message.text):  # تحليل النصوص
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
        
        # تحليل الصورة
        if analyze_image_with_deepai(file_path):
            bot.delete_message(message.chat.id, message.message_id)
            notify_developer(message, "صورة", "🚫 الصورة تحتوي على محتوى غير لائق.")
    except Exception as e:
        print(f"خطأ أثناء استقبال الصورة: {e}")

# ===== تشغيل البوت =====
print("🚀 البوت يعمل الآن...")
bot.infinity_polling()
"""

# تحديث ملف README.md ليشمل معلومات الترحيب ومنع السب والصور
readme_updated = """\
# بوت مراقبة التليجرام 🚀

## **🔹 المميزات:**
✅ **تحليل النصوص ومنع السب** باستخدام **OpenAI**.  
✅ **تحليل الصور ومنع الصور غير اللائقة** باستخدام **DeepAI**.  
✅ **إرسال تقرير للمطور عند اكتشاف أي محتوى مشبوه**.  
✅ **إرسال رسالة ترحيب عند كتابة `/start`**.  
