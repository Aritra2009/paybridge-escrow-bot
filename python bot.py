import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

# ========== ENV VARIABLES ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
PROOF_CHANNEL_ID = int(os.getenv("PROOF_CHANNEL_ID"))

if not BOT_TOKEN or not ADMIN_ID or not PROOF_CHANNEL_ID:
    raise RuntimeError("Environment variables missing!")

# ========== BOT SETUP ==========
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ========== START COMMAND ==========
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 <b>Welcome to PayBridge Escrow</b>\n\n"
        "🔒 Safe • Trusted • Fast\n\n"
        "📌 Commands:\n"
        "/deal – Create escrow deal\n"
        "/help – How escrow works"
    )

# ========== HELP COMMAND ==========
@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "ℹ️ <b>How Escrow Works</b>\n\n"
        "1️⃣ Buyer pays to escrow\n"
        "2️⃣ Seller delivers product\n"
        "3️⃣ Admin releases payment\n\n"
        "💬 Contact admin for support"
    )

# ========== DEAL COMMAND ==========
@dp.message(Command("deal"))
async def deal_cmd(message: types.Message):
    await message.answer(
        "📝 <b>Escrow Deal Started</b>\n\n"
        "Please send:\n"
        "• Buyer username\n"
        "• Seller username\n"
        "• Amount (UPI / Crypto)\n"
        "• Product / Service"
    )

# ========== ADMIN: POST PROOF ==========
@dp.message(Command("proof"))
async def post_proof(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("❌ You are not admin")

    text = message.text.replace("/proof", "").strip()
    if not text:
        return await message.reply("⚠️ Usage:\n/proof Proof message")

    await bot.send_message(
        PROOF_CHANNEL_ID,
        f"✅ <b>Escrow Proof</b>\n\n{text}"
    )

    await message.reply("✅ Proof posted to channel")

# ========== BOT START ==========
async def main():
    print("🤖 Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
