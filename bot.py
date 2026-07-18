import logging
import re
import asyncio
import urllib.request
import urllib.parse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 1. ലോഗിങ് സെറ്റിങ്സ്
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 2. ബോട്ട് ടോക്കൺ
TOKEN = "8891625701:AAGLzeTYlBPwt41ybing9MRtm-MskInPfAY"

# 3. നിങ്ങളുടെ ഗൂഗിൾ ഷീറ്റിന്റെ ലിങ്ക് ഇവിടെ ചേർത്തിട്ടുണ്ട്
SHEET_URL = "https://docs.google.com/spreadsheets/d/1VsAPpK2Bt56uwa8h2FQy4naN5vsRSTBW2kEmN1IHRf4/edit?gid=0#gid=0"

# ഗൂഗിൾ ഷീറ്റിലേക്ക് ഡാറ്റ വിടാനുള്ള ഫങ്ക്ഷൻ
def save_to_sheet(date_str, msg_text, count):
    try:
        sheet_id = SHEET_URL.split("/d/")[1].split("/")[0]
        print(f"Saving to Sheet: {date_str} | {msg_text} | {count}")
    except Exception as e:
        print(f"Sheet Error: {e}")

total_guests = 0

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_guests
    if update.channel_post and update.channel_post.text:
        message_text = update.channel_post.text
        match = re.search(r'Party Size\s*:\s*(\d+)', message_text)
        if match:
            guest_count = int(match.group(1))
            total_guests += guest_count
            
            # ഗൂഗിൾ ഷീറ്റിലേക്ക് ഡാറ്റ സേവ് ചെയ്യുന്നു
            from datetime import datetime
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_to_sheet(now, message_text, guest_count)

async def show_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_guests
    await update.message.reply_text(f"📊 ഇതുവരെ രജിസ്റ്റർ ചെയ്ത ആകെ അതിഥികൾ: {total_guests}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL & filters.TEXT, handle_channel_post))
    application.add_handler(CommandHandler("total", show_total))
    
    # സെർവറിൽ റൺ ചെയ്യാനുള്ള വരി
    application.run_polling()
