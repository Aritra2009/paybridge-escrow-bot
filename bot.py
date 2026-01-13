import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import random

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
PROOF_CHANNEL_ID = int(os.getenv("PROOF_CHANNEL_ID"))
ESCROW_FEE_PERCENT = 5

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class DealState(StatesGroup):
    buyer = State()
    seller = State()
    amount = State()
    payment = State()

deals = {}

def generate_deal_id():
    return f"PB-{random.randint(100000, 999999)}"

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(
        "🔐 *PayBridge Escrow Bot*\n\n"
        "Use /newdeal to start an escrow deal.",
        parse_mode="Markdown"
    )

@dp.message_handler(commands=['newdeal'])
async def newdeal(message: types.Message):
    await message.reply("👤 Buyer username (without @):")
    await DealState.buyer.set()

@dp.message_handler(state=DealState.buyer)
async def buyer_step(message: types.Message, state: FSMContext):
    await state.update_data(buyer=message.text)
    await message.reply("👤 Seller username (without @):")
    await DealState.seller.set()

@dp.message_handler(state=DealState.seller)
async def seller_step(message: types.Message, state: FSMContext):
    await state.update_data(seller=message.text)
    await message.reply("💰 Deal amount:")
    await DealState.amount.set()

@dp.message_handler(state=DealState.amount)
async def amount_step(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("❌ Numbers only")
        return
    await state.update_data(amount=int(message.text))

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("UPI", "Crypto")
    await message.reply("💳 Payment method:", reply_markup=kb)
    await DealState.payment.set()

@dp.message_handler(state=DealState.payment)
async def payment_step(message: types.Message, state: FSMContext):
    if message.text not in ["UPI", "Crypto"]:
        await message.reply("❌ Use keyboard")
        return

    data = await state.get_data()
    deal_id = generate_deal_id()
    fee = round(data['amount'] * ESCROW_FEE_PERCENT / 100, 2)
    total = round(data['amount'] + fee, 2)

    deals[deal_id] = {
        "buyer": data['buyer'],
        "seller": data['seller'],
        "amount": data['amount'],
        "payment": message.text,
    }

    btn = types.InlineKeyboardMarkup()
    btn.add(types.InlineKeyboardButton("✅ Complete Deal", callback_data=f"complete_{deal_id}"))

    await bot.send_message(
        ADMIN_ID,
        f"🆕 *New Deal*\n\n"
        f"🆔 Deal ID: `{deal_id}`\n"
        f"👤 Buyer: @{data['buyer']}\n"
        f"👤 Seller: @{data['seller']}\n"
        f"💰 Amount: {data['amount']}\n"
        f"💳 Payment: {message.text}\n"
        f"💼 Fee: {fee}\n"
        f"🔐 Total: {total}",
        reply_markup=btn,
        parse_mode="Markdown"
    )

    await message.reply(f"✅ Deal created!\nDeal ID: `{deal_id}`", parse_mode="Markdown")
    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith("complete_"))
async def complete_deal(call: types.CallbackQuery):
    deal_id = call.data.split("_")[1]
    deal = deals.get(deal_id)

    if not deal:
        await call.answer("Deal not found", show_alert=True)
        return

    await bot.send_message(
        PROOF_CHANNEL_ID,
        f"✅ *Deal Completed*\n\n"
        f"🆔 Deal ID: `{deal_id}`\n"
        f"👤 Buyer: @{deal['buyer']}\n"
        f"👤 Seller: @{deal['seller']}\n"
        f"💰 Amount: {deal['amount']}\n"
        f"💳 Payment: {deal['payment']}",
        parse_mode="Markdown"
    )

    await call.message.edit_text(f"✅ Deal `{deal_id}` completed & proof posted.")
    deals.pop(deal_id)

if __name__ == "__main__":
    executor.start_polling(dp)
