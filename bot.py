from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# ======================= تنظیمات ==========================
TOKEN = "8316864896:AAHqPwGOpBmjN8PNmMBlL_kFuk6kdM-Psw0"
CHANNEL = "@rat_source_98"
ADMIN_ID = 7608201750
FREE_FILE_ID = "BQACAgQAAxkBAAMFaXr8ynS3BzSnUvIZ3GHk"
PAID_FILE_ID = "FbpW0AsAAqccAAI4C9hTGsx-Krc2InM4BA"
waiting_for_payment = {}
# ==========================================================

# بررسی عضویت در کانال
async def is_member(bot, user_id):
    member = await bot.get_chat_member(CHANNEL, user_id)
    return member.status in ["member", "administrator", "creator"]

# دستور /start
async def start(update, context):
    user_id = update.effective_user.id

    if not await is_member(context.bot, user_id):
        btn = [[InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{CHANNEL[1:]}")]]
        await update.message.reply_text(
            "❌ اول عضو کانال شو بعد دوباره /start رو بزن",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return

    buttons = [
        [InlineKeyboardButton("📘 فایل رایگان", callback_data="free")],
        [InlineKeyboardButton("💰 فایل پولی", callback_data="paid")]
    ]
    await update.message.reply_text(
        "📂 فایل مورد نظر رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# هندل دکمه‌ها
async def buttons(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "free":
        await context.bot.send_document(
            chat_id=query.message.chat.id,
            document=FREE_FILE_ID
        )

    elif query.data == "paid":
        waiting_for_payment[query.from_user.id] = True
        await query.message.reply_text(
            "💰 قیمت فایل: 50,000 تومان\n"
            "💳 کارت به کارت:\n"
            "6037-xxxx-xxxx-xxxx\n"
            "👤 بعد از پرداخت، عکس رسید رو همین‌جا بفرست"
        )

# هندل رسید پرداخت
async def payment_receipt(update, context):
    user_id = update.effective_user.id
    if user_id in waiting_for_payment and update.message.photo:
        waiting_for_payment.pop(user_id)
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=f"رسید پرداخت از کاربر {user_id}\nبرای تایید بزن: /ok_{user_id}"
        )
        await update.message.reply_text(
            "✅ رسید دریافت شد\nبعد از تایید ادمین، فایل ارسال می‌شود"
        )

# تایید پرداخت ادمین
async def confirm_payment(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    if update.message.text.startswith("/ok_"):
        user_id = int(update.message.text.replace("/ok_", ""))
        await context.bot.send_document(
            chat_id=user_id,
            document=PAID_FILE_ID
        )
        await update.message.reply_text("✅ فایل برای کاربر ارسال شد")

# ==================== اجرای ربات ===========================
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.PHOTO, payment_receipt))
app.add_handler(CommandHandler("ok_", confirm_payment))

app.run_polling()
# ============================================================
