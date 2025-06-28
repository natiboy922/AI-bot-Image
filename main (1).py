import os
import asyncio
import logging
import replicate
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(level=logging.INFO)

# Get tokens from environment variables (Render style)
REPLICATE_API_TOKEN = os.environ.get("r8_CMbAr4mSjnTJKYexBD4kDZiaPg2Pn0s2hq74e")
TELEGRAM_BOT_TOKEN = os.environ.get("8024591512:AAHDJfkd4qroZHPIcuA4mPlGg6BUVdV80U0")  # IMPORTANT for Render

# Make sure tokens exist
if not TELEGRAM_BOT_TOKEN or not REPLICATE_API_TOKEN:
    raise Exception("❌ Missing environment variables: TOKEN or REPLICATE_API_TOKEN")

client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Just send me a text prompt I’ll generate an AI image for you!❤️😊")

# Handle regular text messages
async def generate_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.strip()
    if prompt.startswith("/") or not prompt:
        return

    loading_msg = await update.message.reply_text("⏳ Generating image...")

    try:
        for _ in range(3):
            for dots in [".", "..", "..."]:
                await loading_msg.edit_text(f"⏳ Generating image{dots}")
                await asyncio.sleep(0.5)

        input_data = {
            "width": 1024,
            "height": 1024,
            "prompt": prompt,
            "refine": "expert_ensemble_refiner",
            "apply_watermark": False,
            "num_inference_steps": 25
        }

        output = client.run(
            "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
            input=input_data
        )

        image_url = str(output[0])
        image_data = requests.get(image_url).content

        await loading_msg.edit_text("✅ Image generated!🎉")
        await update.message.reply_photo(photo=image_data, caption=f"🖼️ Prompt: {prompt}")

    except Exception as e:
        await loading_msg.edit_text(f"❌ Error: {e}")

# Start bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_from_text))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
