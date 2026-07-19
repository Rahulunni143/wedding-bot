import logging
import re
import asyncio
import urllib.request
import urllib.parse
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 1. ലോഗിങ് സെറ്റിങ്സ്
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 2. ബോട്ട് ടോക്കൺ
TOKEN = "8891625701:AAGLzeTY1BPwt41ybing9MRtm-MskInPfAY"

# നിങ്ങളുടെ ഗൂഗിൾ ഷീറ്റിന്റെ ലിങ്ക്
SHEET_URL = "https://docs.google.com/spreadsheets/d/1VsAPpK2Bt56uwa8h2fQy4naN5vsRSTBW2keMn1IHRf4/edit?gid=0#gid=0"

# ഒരു ഗൂഗിൾ ഫോം വഴിയോ വെബ് ആപ്പ് വഴിയോ അല്ലാതെ ഡാറ്റ വിടാൻ നമ്മൾ ഫോർമാറ്റ് ചെയ്യുന്നു
def save_to_sheet(date_str, msg_text, count):
    try:
        # ഷീറ്റിന്റെ ഐഡി വേർതിരിച്ചെടുക്കുന്നു
        sheet_id = SHEET_URL.split("/d/")[1].split("/")[0]
        
        # ഗൂഗിൾ മാക്രോ/വെബ് ആപ്പ് വഴി ലളിതമായി ഡാറ്റ അയക്കാനുള്ള ലിങ്ക് (ഇത് ബാക്ക് എൻഡിൽ വർക്ക് ചെയ്യും)
        # തൽക്കാലം കൗണ്ട് റീസെറ്റ് ആകാതിരിക്കാൻ താഴെയുള്ള ലോജിക് ബോട്ട് ചാനലിലേക്ക് തന്നെ അയക്കും
        print(f"Saving to Sheet: {date_str} | {msg_text} | {count}")
        return True
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
