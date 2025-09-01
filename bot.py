import logging
import sqlite3
import time
import uuid
import json
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Import settings from config.py
from config import (
    POINTS_PER_AD,
    DAILY_ADS_LIMIT,
    ADS_COOLDOWN_PERIOD_SECONDS,
    REFERRAL_POINTS,
    DAILY_BONUS_POINTS,
    MINIMUM_WITHDRAWAL_POINTS,
    POINTS_TO_USDT_RATE,
    ADMIN_USER_ID
)

BOT_TOKEN = "7771736139:AAFhBdAAZF6-rV7YCX08hHK_FAYrHDe8sL0"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Database functions ---
def get_db_connection():
    return sqlite3.connect('earning_bot.db')

def get_user_data(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user = cursor.fetchone()
    conn.close()
    return user

def update_user_points(user_id, points_to_add):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points_to_add, user_id))
    conn.commit()
    conn.close()

def update_user_ad_count(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET ads_watched_today = ads_watched_today + 1, last_ad_time = ? WHERE user_id = ?",
        (int(time.time()), user_id)
    )
    conn.commit()
    conn.close()

def get_or_create_referral_code(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT referral_code FROM users WHERE user_id=?", (user_id,))
    code = cursor.fetchone()
    if not code or not code[0]:
        new_code = str(uuid.uuid4())[:8]
        cursor.execute("UPDATE users SET referral_code=? WHERE user_id=?", (new_code, user_id))
        conn.commit()
        code = (new_code,)
    conn.close()
    return code[0]

def set_referrer(user_id, referrer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT referred_by FROM users WHERE user_id=?", (user_id,))
    referred_by = cursor.fetchone()
    if not referred_by or not referred_by[0]:
        cursor.execute("UPDATE users SET referred_by=? WHERE user_id=?", (referrer_id, user_id))
        conn.commit()
        update_user_points(referrer_id, REFERRAL_POINTS)
        return True
    return False

def update_user_last_bonus_time(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET last_bonus_time = ? WHERE user_id = ?", (int(time.time()), user_id))
    conn.commit()
    conn.close()

# --- Keyboard Markups ---
language_keyboard = [[KeyboardButton("English"), KeyboardButton("")]]
language_markup = ReplyKeyboardMarkup(language_keyboard, one_time_keyboard=True, resize_keyboard=True)

# Replace "YOUR_VERCEL_URL_HERE" with the URL from Vercel/Netlify
VERCEL_URL = "_Vercel_URL__"

english_menu_keyboard = [
    [KeyboardButton(" Watch Ads", web_app=WebAppInfo(url=VERCEL_URL))],
    [KeyboardButton(" Daily Bonus"), KeyboardButton(" Leaderboard")],
    [KeyboardButton(" Refer & Earn"), KeyboardButton(" Withdraw")],
    [KeyboardButton(" Settings")]
]
english_menu_markup = ReplyKeyboardMarkup(english_menu_keyboard, resize_keyboard=True)

bangla_menu_keyboard = [
    [KeyboardButton("  ", web_app=WebAppInfo(url=VERCEL_URL))],
    [KeyboardButton("  "), KeyboardButton(" ")],
    [KeyboardButton("   "), KeyboardButton(" ")],
    [KeyboardButton(" ")]
]
bangla_menu_markup = ReplyKeyboardMarkup(bangla_menu_keyboard, resize_keyboard=True)

# --- Handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    get_user_data(user_id)
    
    if context.args and len(context.args) == 1:
        referrer_code = context.args[0]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE referral_code=?", (referrer_code,))
        referrer_id_result = cursor.fetchone()
        conn.close()

        if referrer_id_result:
            referrer_id = referrer_id_result[0]
            if str(user_id) != str(referrer_id):
                if set_referrer(user_id, referrer_id):
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=f" Congratulations! A new user joined using your referral link. You earned **{REFERRAL_POINTS}** points!",
                    )
    
    await update.message.reply_text(
        "Please select your language from the keyboard:",
        reply_markup=language_markup,
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    
    if user_message == "English":
        await update.message.reply_text("You have selected English. Here are your options:", reply_markup=english_menu_markup)
        return
    elif user_message == "":
        await update.message.reply_text("          :", reply_markup=bangla_menu_markup)
        return
    
    if user_message == " Daily Bonus" or user_message == "  ":
        await daily_bonus_handler(update, context)
    elif user_message == " Refer & Earn" or user_message == "   ":
        await refer_and_earn_handler(update, context)
    elif user_message == " Leaderboard" or user_message == " ":
        await update.message.reply_text("This is the Leaderboard section. Coming soon!")
    elif user_message == " Withdraw" or user_message == " ":
        await update.message.reply_text("This is the Withdraw section. Coming soon!")
    elif user_message == " Settings" or user_message == " ":
        await update.message.reply_text("This is the Settings section. Coming soon!")
    else:
        await update.message.reply_text("I didn't understand. Please use the menu buttons.")
    
async def daily_bonus_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT last_bonus_time FROM users WHERE user_id = ?", (user_id,))
    last_bonus_time = cursor.fetchone()[0]
    conn.close()

    if (time.time() - last_bonus_time) > 86400: # 24 hours in seconds
        update_user_points(user_id, DAILY_BONUS_POINTS)
        update_user_last_bonus_time(user_id)
        await update.message.reply_text(f" Congratulations! You have received your daily bonus of **{DAILY_BONUS_POINTS}** points!")
    else:
        remaining_time = int(86400 - (time.time() - last_bonus_time))
        hours = remaining_time // 3600
        minutes = (remaining_time % 3600) // 60
        await update.message.reply_text(f" You have already claimed your daily bonus. Please wait {hours} hours and {minutes} minutes to claim it again.")

async def refer_and_earn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    referral_code = get_or_create_referral_code(user_id)
    
    referral_link = f"https://t.me/{context.bot.username}?start={referral_code}"
    
    await update.message.reply_text(
        f" Share your referral link with your friends to earn **{REFERRAL_POINTS}** points for each new user who joins!\n\n Your Referral Link:\n`{referral_link}`",
        parse_mode="Markdown"
    )

async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    current_points = user_data[1]
    
    await update.message.reply_text(f" Your current balance is **{current_points}** points.")

async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    web_app_data = json.loads(update.effective_message.web_app_data.data)
    
    if web_app_data.get('action') == 'claim_ad_points':
        # Check if the user is eligible for points
        user_data = get_user_data(user_id)
        ads_watched = user_data[2]
        last_ad_time = user_data[3]

        if (time.time() - last_ad_time) > 86400:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET ads_watched_today = 0 WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            ads_watched = 0

        if ads_watched >= DAILY_ADS_LIMIT:
            await update.message.reply_text(" You have reached your daily ad limit. Please try again tomorrow.")
            return

        if ads_watched % 30 == 0 and ads_watched != 0:
            if (time.time() - last_ad_time) < ADS_COOLDOWN_PERIOD_SECONDS:
                remaining_time = int(ADS_COOLDOWN_PERIOD_SECONDS - (time.time() - last_ad_time))
                minutes = remaining_time // 60
                seconds = remaining_time % 60
                await update.message.reply_text(f" Cooldown in progress. Please wait for {minutes} minutes and {seconds} seconds.")
                return
        
        # Award points as the user has "watched" the ad
        update_user_points(user_id, POINTS_PER_AD)
        update_user_ad_count(user_id)
        await update.message.reply_text(f" Congratulations! You have earned **{POINTS_PER_AD}** points!")


# Define the main function to run the bot
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("balance", check_balance))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
    