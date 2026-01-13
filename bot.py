import os
import logging
from aiogram import Bot, Dispatcher, executor, types

# ===== ENV VARIABLES =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
PROOF_CHANNEL_ID = int(os.getenv("PROOF_CHANNEL_ID"))

# ===== LOGGING =====
logging.basicConfig(level=logging.INFO)

# ===== BOT INIT =====
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


# ===== START COMMAND =====
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.reply(
        "🤝 <b>Welcome to PayBridge Escrow</b>\n\n"
        "🔐 Secure escrow for UPI & Crypto\n"
        "👨‍💼 Admin protected deals\n\n"
        "Type /help to see options"
    )


# ===== HELP COMMAND =====
@dp.message_handler(commands=["help"])
async def help_cmd(message: types.Message):
    await message.reply(
        "📌 <b>Available Commands</b>\n\n"
        "/start – Start bot\n"
        "/help – Help menu\n"
        "/admin – Admin panel (admin only)"
    )


# ===== ADMIN PANEL =====
@dp.message_handler(commands=["admin"])
async def admin_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("❌ You are not authorized.")

    await message.reply(
        "🛠 <b>Admin Panel</b>\n\n"
        "✅ Bot is running\n"
        "📢 Proof channel connected"
    )


# ===== BOT START =====
if __name__ == "__main__":
    print("🤖 Bot started...")
    executor.start_polling(dp, skip_updates=True)
