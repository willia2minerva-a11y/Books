# services/telegram_ops.py
import os
import aiohttp
from core.models import Product

class TelegramDispatcher:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    async def send_launch_package(self, product: Product) -> bool:
        """إرسال الكتاب مع خطة التسويق كحزمة واحدة"""
        if not self.bot_token or not self.chat_id:
            return False

        if not product.file_path or not os.path.exists(product.file_path):
            return False

        # تجهيز رسالة التسويق الاحترافية
        caption = f"🚀 *تم إطلاق منتج جديد!*\n\n"
        caption += f"🏷️ *النيش:* {product.niche}\n"
        caption += f"📚 *النوع:* {product.product_type}\n\n"
        caption += f"✨ *العنوان المقترح (SEO):*\n`{product.seo_title}`\n\n"
        caption += f"🔑 *الكلمات المفتاحية:*\n`{product.keywords}`"

        try:
            async with aiohttp.ClientSession() as session:
                # 1. إرسال المستند (الـ PDF)
                url_doc = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
                with open(product.file_path, 'rb') as f:
                    form_data = aiohttp.FormData()
                    form_data.add_field('chat_id', self.chat_id)
                    form_data.add_field('document', f, filename=os.path.basename(product.file_path))
                    form_data.add_field('caption', caption)
                    form_data.add_field('parse_mode', 'Markdown')
                    
                    async with session.post(url_doc, data=form_data) as response:
                        if response.status != 200:
                            return False

                # 2. إرسال سكريبت التيك توك والوصف في رسالة منفصلة
                url_msg = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                marketing_msg = f"📝 *وصف أمازون:*\n{product.description}\n\n"
                marketing_msg += f"🎬 *سكريبت تيك توك:*\n{product.tiktok_script}"
                
                payload = {
                    "chat_id": self.chat_id,
                    "text": marketing_msg,
                    "parse_mode": "Markdown"
                }
                async with session.post(url_msg, json=payload) as response:
                    return response.status == 200

        except Exception as e:
            print(f"Telegram Error: {e}")
            return False

telegram_dispatcher = TelegramDispatcher()

