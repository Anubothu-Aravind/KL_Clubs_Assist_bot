# At the top of your file, add:
import os
from dotenv import load_dotenv

load_dotenv()

# Replace the BOT_TOKEN line with:
BOT_TOKEN = os.getenv('BOT_TOKEN')
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Replace 'YOUR_BOT_TOKEN' with your actual BotFather token
BOT_TOKEN = '8191672884:AAHNTDNNyGStchaMCFdWzfsOfrehhsyEHLg'

# Define a list of clubs
clubs = [
    "Aprameya Club", "Broadband Networks Club", "Design Circle", "Expedite Club",
    "Garuda-Drone Technology Club", "Google Developer Groups", "Intel Innovation",
    "Kognitiv Club", "Mayavi Technology Club", "Megha – The Cloud Computing Club",
    "Robotic Process Automation", "Software Engineers Associates(SEA)",
    "School of Competitive Coding", "School of Data Science", "Trailblazers club",
    "White Hat Hackers"
]


# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = "Welcome to KL Clubs Assistance Bot! Use /clubs to see the list of clubs or /help for assistance."
    await update.message.reply_text(welcome_message)


# /help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = (
        "Here are the available commands:\n"
        "/start - Start the bot\n"
        "/help - Get help with the bot\n"
        "/clubs - Show list of clubs"
    )
    await update.message.reply_text(help_message)


# /clubs command handler
async def clubs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(club, callback_data=club)] for club in clubs]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Here is the list of Clubs :", reply_markup=reply_markup)


# Handle club selection and open submenus if necessary
async def handle_club_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "Kognitiv Club":
        # Add submenu options for "Kognitiv Club"
        submenu_keyboard = [
            [InlineKeyboardButton("Website", url="https://kognitivclub.tech/")],
            [InlineKeyboardButton("Submenu Option 2", callback_data="Kognitiv_Option2")],
            [InlineKeyboardButton("Back to Clubs", callback_data="back_to_clubs")]
        ]
        reply_markup = InlineKeyboardMarkup(submenu_keyboard)
        await query.edit_message_text("Kognitiv Club Options:", reply_markup=reply_markup)

    elif query.data == "back_to_clubs":
        # Go back to the main club selection menu
        keyboard = [[InlineKeyboardButton(club, callback_data=club)] for club in clubs]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select a club:", reply_markup=reply_markup)

    else:
        # Display a message for selected clubs
        await query.edit_message_text(f"You selected {query.data}.")


# Main function to set up the bot and handlers
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clubs", clubs_command))

    # Register a handler for callback queries from inline buttons
    app.add_handler(CallbackQueryHandler(handle_club_selection))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
