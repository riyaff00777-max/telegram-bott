import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import BOT_TOKEN, ADMIN_ID

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, coins INTEGER)")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT coins FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()
    if data is None:
        cursor.execute("INSERT INTO users VALUES (?,?)", (user_id, 0))
        conn.commit()
        return 0
    return data[0]

def add_coins(user_id, amount):
    coins = get_user(user_id) + amount
    cursor.execute("UPDATE users SET coins=? WHERE user_id=?", (coins, user_id))
    conn.commit()

def use_coins(user_id, amount):
    coins = get_user(user_id)
    if coins < amount:
        return False
    cursor.execute("UPDATE users SET coins=? WHERE user_id=?", (coins - amount, user_id))
    conn.commit()
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Welcome to Like Exchange Bot\nEarn coins: /earn\nSend likes: /like UID")

async def earn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    add_coins(user_id, 10)
    await update.message.reply_text("✅ You earned 10 coins!")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = get_user(update.message.from_user.id)
    await update.message.reply_text(f"💰 Your Coins: {coins}")

async def like(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        uid = context.args[0]
    except:
        await update.message.reply_text("Usage: /like UID")
        return

    if not use_coins(user_id, 10):
        await update.message.reply_text("❌ Not enough coins! Use /earn")
        return

    await update.message.reply_text(f"❤️ Likes sent to {uid} (Exchange System)")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    await update.message.reply_text(f"👑 Admin Panel\nUsers: {total}")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("earn", earn))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("like", like))
app.add_handler(CommandHandler("admin", admin))

app.run_polling()
