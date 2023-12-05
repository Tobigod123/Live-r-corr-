import telegram
from telegram.ext import Updater, CommandHandler
import subprocess
import logging
import argparse
import os
from datetime import datetime

# Telegram bot token
TOKEN = 'YOUR_BOT_TOKEN'

# List of authorized user IDs
AUTHORIZED_IDS = [YOUR_AUTHORIZED_USER_IDS]

# Initialize the Telegram bot
bot = telegram.Bot(token=TOKEN)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Define the start command handler
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the Advanced IPTV Recorder Bot!")

# Define the help command handler
def help_command(update, context):
    help_text = """
    Welcome to the Advanced IPTV Recorder Bot!

    Commands:
    /start - Start the bot
    /record <iptv_link> <start_time> <end_time> - Record IPTV stream
    /help - Show this help message
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

# Define the record command handler
def record(update, context):
    try:
        # Check if user is authorized
        user_id = update.effective_user.id
        if user_id not in AUTHORIZED_IDS:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, you are not authorized to use this bot.")
            return

        # Create 'recordings' directory if it doesn't exist
        if not os.path.exists('recordings'):
            os.makedirs('recordings')
            os.mkdir('recordings')

        # Parse command arguments from message text
        command_args = update.message.text.split()[1:]
        parser = argparse.ArgumentParser(description='Advanced IPTV Recorder Bot')
        parser.add_argument('iptv_link', help='IPTV link to record')
        parser.add_argument('start_time', help='Start time for recording')
        parser.add_argument('end_time', help='End time for recording')
        args = parser.parse_args(command_args)

        # Perform the live recording using FFMPEG with advanced settings
        output_file = f'recordings/{user_id}_{datetime.now().strftime("%Y%m%d%H%M%S")}.mp4'
        subprocess.run(['ffmpeg', '-i', args.iptv_link, '-ss', args.start_time, '-to', args.end_time,
                        '-c:v', 'libx264', '-preset', 'veryfast', '-metadata', 'title=World famous cartoon',
                        '-c:a', 'aac', '-b:a', '50k', output_file])

        # Check file size before sending
        file_size = os.path.getsize(output_file)
        if file_size > 2 * 1024 * 1024 * 1024:  # 2 GB limit for non-bot users
            context.bot.send_message(chat_id=update.effective_chat.id, text="The recorded video exceeds the maximum file size limit.")
        else:
            # Send the recorded video file to the user
            context.bot.send_video(chat_id=update.effective_chat.id, video=open(output_file, 'rb'))

    except argparse.ArgumentError:
        # Handle argument parsing error
        context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid arguments. Please check your input and try again.")

    except subprocess.CalledProcessError as e:
        # Log the FFMPEG error details
        logging.error(f"FFMPEG error: {e}")
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"An error occurred during FFMPEG execution: {str(e)}")

    except Exception as e:
        # Log the exception
        logging.error(f"An error occurred: {e}")

        # Send a more informative error message to the user
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"An unexpected error occurred: {str(e)}")

# Create an instance of the Telegram updater
updater = Updater(token=TOKEN, use_context=True)

# Get the dispatcher to register handlers
dispatcher = updater.dispatcher

# Register the start command handler
dispatcher.add_handler(CommandHandler('start', start))

# Register the help command handler
dispatcher.add_handler(CommandHandler('help', help_command))

# Register the record command handler
dispatcher.add_handler(CommandHandler('record', record))

# Start the bot
updater.start_polling()

# Run the bot until you send a signal to stop it
updater.idle()
