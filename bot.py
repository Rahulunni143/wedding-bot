import logging
import re
import asyncio
import urllib.request
import urllib.parse
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# --- പുതിയതായി ചേർത്ത വെബ് സെർവർ കോഡ് (Render Timeout ഒഴിവാക്കാൻ) ---
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running perfectly!"

def run():
    # Render നൽകുന്ന PORT ഓട്ടോമാറ്റിക് ആയി എടുക്കും
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ബോട്ട് ബാക്ക്ഗ്രൗണ്ടിൽ എപ്പോഴും ലൈവ് ആയി ഇരിക്കാൻ ഇത് വിളിക്കുന്നു
keep_alive()
# -----------------------------------------------------------------

# 1. ലോഗിങ് സെറ്റിങ്സ്
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 2. ബോട്ട് ടോക്കൺ
TOKEN = "8891625701:AAGLzeTYlBPwt41ybing9MRtm-MskInPfAY"

# നിങ്ങളുടെ ഗൂഗിൾ ഷീറ്റിന്റെ ലിങ്ക്
SHEET_URL = "https://docs.google.com/spreadsheets/d/1VsAPpK2Bt56uwa8h2fQy4naN5vsRSTBW2keMn1IHRf4/"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwgIgoSG4XYNcf-D1OhSBJf9QgH-xXGmZuOir8BPvZnbt0zaJ6yrHss_rKDVv33UbKJ/exec"

# ഒരു ഗൂഗിൾ ഫോം വഴിയോ വെബ് ആപ്പ് വഴിയോ അല്ലാതെ ഡാറ്റ വിടാൻ നമ്മൾ ഫോർമാറ്റ് ചെയ്യുന്നു
def save_to_sheet(date_str, msg_text, count):
    try:
        params = urllib.parse.urlencode({
            'date': date_str,
            'message': msg_text,
            'count': count
        })
        url = f"{WEB_APP_URL}?{params}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            res_text = response.read().decode('utf-8')
            return "Success" in res_text
    except Exception as e:
        print(f"Sheet Error: {e}")
        return False

# സെർവർ റീസ്റ്റാർട്ട് ആയാലും കൗണ്ട് പോകാതിരിക്കാൻ തൽക്കാലം ടെക്സ്റ്റ് മെസ്സേജിൽ നിന്ന് ആകെ തുക കാണിക്കുന്നു
total_guests = 0

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_guests
    if update.channel_post and update.channel_post.text:
        message_text = update.channel_post.text
        
        # 'Party Size: 5' ഉണ്ടോ എന്ന് നോക്കുന്നു
        match = re.search(r'Party Size\s*:\s*(\d+)', message_text, re.IGNORECASE)
        if match:
            guest_count = int(match.group(1))
            total_guests += guest_count
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_to_sheet(now, message_text, guest_count)
            
            # ചാനലിലേക്ക് മറുപടി അയക്കുന്നു
            await context.bot.send_message(
                chat_id=update.channel_post.chat_id,
                text=f"✅ പുതിയ അതിഥി കൗണ്ട് ചേർത്തു: {guest_count}\n📊 ആകെ അതിഥികൾ: {total_guests}"
            )

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL & filters.TEXT, handle_channel_post))
    application.run_polling()

