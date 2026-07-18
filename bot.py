import logging
import re
import asyncio
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 1. ലോഗിങ് സെറ്റിങ്സ്
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 2. ടോക്കൺ
TOKEN = "8891625701:AAGLzeTY1BPwt41ybing9MRtm-MskInPfAY"

# 3. ഗൂഗിൾ ഷീറ്റ് കണക്ഷൻ ഫങ്ക്ഷൻ
def get_sheet():
    # Render-ന്റെ Environment Variables-ൽ നിന്ന് credentials എടുക്കുന്നു
    import json
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS environment variable is missing!")
        
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=scopes)
    client = gspread.authorize(creds)
    
    # നിങ്ങളുടെ ഷീറ്റിന്റെ ID
    sheet_id = "1VsAPpK2Bt56uwa8h2fQy4naN5vsRSTBW2keMn1IHRf4"
    return client.open_by_key(sheet_id).sheet1

def save_to_sheet(date_str, msg_text, count):
    try:
        sheet = get_sheet()
        # ഷീറ്റിലെ അടുത്ത വരിയിലേക്ക് ഡാറ്റ ചേർക്കുന്നു (Append)
        sheet.append_row([date_str, msg_text, count])
        return True
    except Exception as e:
        logging.error(f"Sheet Save Error: {e}")
        return False

def get_total_guests():
    try:
        sheet = get_sheet()
        # C കോളത്തിലെ (Count) എല്ലാ വാല്യൂടെയും ലിസ്റ്റ് എടുക്കുന്നു
        counts = sheet.col_values(3)[1:] # ഹെഡർ (Count) ഒഴിവാക്കാൻ ആദ്യ വരി മാറ്റുന്നു
        total = 0
        for c in counts:
            try:
                total += int(c)
            except ValueError:
                continue
        return total
    except Exception as e:
        logging.error(f"Get Total Error: {e}")
        return 0

# 4. മെസ്സേജ് ഹാൻഡ്‌ലർ
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.text:
        message_text = update.channel_post.text
        
        # 'Party Size: 5' അല്ലെങ്കിൽ 'Party Size:5' എന്ന് ചെക്ക് ചെയ്യുന്നു
        match = re.search(r'Party Size\s*:\s*(\d+)', message_text, re.IGNORECASE)
        if match:
            guest_count = int(match.group(1))
            
            # കറക്റ്റ് സമയം എടുക്കുന്നു
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # ഷീറ്റിലേക്ക് സേവ് ചെയ്യുന്നു
            saved = save_to_sheet(now, message_text, guest_count)
            
            if saved:
                # ഷീറ്റിൽ നിന്നുള്ള കൃത്യമായ ടോട്ടൽ കൗണ്ട് എടുക്കുന്നു
                current_total = get_total_guests()
                
                # ചാനലിലേക്ക് മറുപടി അയക്കുന്നു
                await context.bot.send_message(
                    chat_id=update.channel_post.chat_id,
                    text=f"✅ ഡാറ്റ ഷീറ്റിലേക്ക് സേവ് ചെയ്തു!\n\nഇതുവരെ രജിസ്റ്റർ ചെയ്ത ആകെ അതിഥികൾ: {current_total}"
                )

async def show_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_total = get_total_guests()
    await update.message.reply_text(f"📊 ഇതുവരെ രജിസ്റ്റർ ചെയ്ത ആകെ അതിഥികൾ: {current_total}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    # ചാനൽ പോസ്റ്റുകൾ റീഡ് ചെയ്യാൻ
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL & filters.TEXT, handle_channel_post))
    # /total കമാൻഡ് വർക്ക് ചെയ്യാൻ
    application.add_handler(CommandHandler("total", show_total))
    
    application.run_polling()
