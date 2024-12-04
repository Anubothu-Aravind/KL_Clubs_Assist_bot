import os
import random
import smtplib
import sqlite3
from keep_alive import keep_alive
from email.message import EmailMessage
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")
ADMIN_ID = 1053930705  # Replace with your Telegram ID

# States for the conversation handler
ADDING_CLUB = 1
VERIFY_OTP = 2

# OTP storage
otp_storage = {}

# SQLite setup
DATABASE_FILE = "clubs.db"

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Clubs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cname TEXT NOT NULL,
            weblink TEXT,
            linkedin TEXT,
            instagram TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Helper to send emails
def send_email(subject, body, recipient):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = "Welcome to KL Clubs Assistance Bot! Use /clubs to see the list of clubs or /help for assistance."
    await update.message.reply_text(welcome_message)

# Help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = (
        "Here are the available commands:\n"
        "/start - Start the bot\n"
        "/help - Get help with the bot\n"
        "/clubs - Show list of clubs\n"
        "/add_club - Request to add a new club"
    )
    await update.message.reply_text(help_message)

# Display Clubs
async def clubs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT cname FROM Clubs")
    club_names = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Ensure updated list is fetched every time
    if not club_names:
        await update.message.reply_text("No clubs available.")
        return

    keyboard = [[InlineKeyboardButton(club, callback_data=club)] for club in club_names]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Here is the list of Clubs:", reply_markup=reply_markup)

# Handle Club Selection
async def handle_club_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    club_name = query.data
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Clubs WHERE cname = ?", (club_name,))
    club = cursor.fetchone()
    conn.close()

    if club:
        cname, weblink, linkedin, instagram = club[1:]
        submenu_keyboard = []
        if weblink:
            submenu_keyboard.append([InlineKeyboardButton("Website", url=weblink)])
        if linkedin:
            submenu_keyboard.append([InlineKeyboardButton("LinkedIn", url=linkedin)])
        if instagram:
            submenu_keyboard.append([InlineKeyboardButton("Instagram", url=instagram)])
        submenu_keyboard.append([InlineKeyboardButton("Back to Clubs", callback_data="back_to_clubs")])

        reply_markup = InlineKeyboardMarkup(submenu_keyboard)
        await query.edit_message_text(f"{club_name} Options:", reply_markup=reply_markup)

    elif query.data == "back_to_clubs":
        await clubs_command(query, context)

# Add Club Command
async def add_club_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please provide your email and club details in the following format:\n\n"
                                    "YourEmail, Club Name, Website Link, LinkedIn Link, Instagram Link")
    return ADDING_CLUB

# Verify Email and Send OTP
async def verify_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.split(",")
    if len(user_input) != 5:
        await update.message.reply_text("Invalid format. Please provide all details.")
        return ADDING_CLUB

    email, club_name, website, linkedin, instagram = map(str.strip, user_input)
    otp = str(random.randint(100000, 999999))
    otp_storage[email] = {"otp": otp, "details": user_input}

    send_email("Verify Your Email", f"Your OTP is: {otp}", email)
    await update.message.reply_text(f"An OTP has been sent to {email}. Please reply with the OTP to verify.")
    return VERIFY_OTP

# Verify OTP
async def verify_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    otp = update.message.text.strip()
    for email, data in otp_storage.items():
        if data["otp"] == otp:
            user_details = data["details"]
            subject = "New Club Registration Request"
            body = (
                f"A new club registration has been requested:\n\n"
                f"Club Name: {user_details[1]}\n"
                f"Website: {user_details[2]}\n"
                f"LinkedIn: {user_details[3]}\n"
                f"Instagram: {user_details[4]}\n\n"
                f"Reply with YES to approve or NO to reject."
            )
            send_email(subject, body, EMAIL_ADDRESS)
            del otp_storage[email]
            otp_storage["latest_request"] = {"details": user_details}
            await update.message.reply_text("Email verified. Request sent to the admin for approval.")
            return ConversationHandler.END

    await update.message.reply_text("Invalid OTP. Please try again.")
    return VERIFY_OTP

# Admin Approval
def process_admin_response(email_body):
    response = email_body.strip().upper()
    user_details = otp_storage.get("latest_request", {}).get("details")

    if not user_details:
        return "No pending requests found!"

    if response == "YES":
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Clubs (cname, weblink, linkedin, instagram) VALUES (?, ?, ?, ?)",
            user_details[1:],
        )
        conn.commit()
        conn.close()
        del otp_storage["latest_request"]
        return "Club added successfully!"
    elif response == "NO":
        del otp_storage["latest_request"]
        return "Club registration request rejected."
    else:
        return "Invalid admin response. Please reply with YES or NO."

# Main Function
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clubs", clubs_command))
    app.add_handler(CallbackQueryHandler(handle_club_selection))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_club", add_club_command)],
        states={
            ADDING_CLUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_email)],
            VERIFY_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_otp)],
        },
        fallbacks=[],
    )
    app.add_handler(conv_handler)
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
    keep_alive()
