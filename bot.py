import os
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

clubs = [
    "Aprameya Club", "Broadband Networks Club", "Design Circle", "Expedite Club",
    "Garuda-Drone Technology Club", "Google Developer Groups", "Intel Innovation",
    "Kognitiv Club", "Mayavi Technology Club", "Megha – The Cloud Computing Club",
    "Robotic Process Automation", "Software Engineers Associates(SEA)",
    "School of Competitive Coding", "School of Data Science", "Trailblazers club",
    "White Hat Hackers"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = "Welcome to KL Clubs Assistance Bot! Use /clubs to see the list of clubs or /help for assistance."
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = (
        "Here are the available commands:\n"
        "/start - Start the bot\n"
        "/help - Get help with the bot\n"
        "/clubs - Show list of clubs"
    )
    await update.message.reply_text(help_message)

async def clubs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(club, callback_data=club)] for club in clubs]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Here is the list of Clubs :", reply_markup=reply_markup)

async def handle_club_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "Kognitiv Club":
        submenu_keyboard = [
            [InlineKeyboardButton("Website", url="https://kognitivclub.tech/")],
            [InlineKeyboardButton("Submenu Option 2", callback_data="Kognitiv_Option2")],
            [InlineKeyboardButton("Back to Clubs", callback_data="back_to_clubs")]
        ]
        reply_markup = InlineKeyboardMarkup(submenu_keyboard)
        await query.edit_message_text("Kognitiv Club Options:", reply_markup=reply_markup)

    elif query.data == "back_to_clubs":
        keyboard = [[InlineKeyboardButton(club, callback_data=club)] for club in clubs]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select a club:", reply_markup=reply_markup)

    else:
                await query.edit_message_text(f"You selected {query.data}.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clubs", clubs_command))
    app.add_handler(CallbackQueryHandler(handle_club_selection))
    print("Bot is running...")
    app.run_polling()
    
if __name__ == "__main__":
    keep_alive()  
    main()
