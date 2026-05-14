# services/image_generator.py
import asyncio
import aiohttp
import random
import urllib.parse
import os

class AsyncImageGenerator:
    """محرك توليد الصور غير المتزامن للسرعة القصوى"""
    
    def __init__(self, temp_dir="temp_assets"):
        self.temp_dir = temp_dir
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            
    async def _fetch_and_save_image(self, session: aiohttp.ClientSession, prompt: str, filename: str, style: str, retries=3) -> bool:
        """جلب صورة واحدة وحفظها مع نظام معالجة الأخطاء والمحاولة التلقائية"""
        
        # هندسة الأوامر (Prompt Engineering) لضمان جودة KDP
        style_prompts = {
            "cover": f"Professional high quality children book cover, {prompt}, vibrant, magical, 8k resolution, NO TEXT, NO WORDS",
            "coloring": f"Pure black and white line art, {prompt}, thick bold outlines, pure white background, NO shading, grayscale, vector style, coloring page for kids",
            "story": f"Children book illustration, {prompt}, colorful, whimsical, disney style, cute"
        }
        
        full_prompt = style_prompts.get(style, prompt)
        encoded_prompt = urllib.parse.quote(full_prompt)
        
        # إضافة seed عشوائي لضمان عدم تكرار الصور
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={random.randint(1, 999999)}"
        filepath = os.path.join(self.temp_dir, filename)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        for attempt in range(retries):
            try:
                # وضع مهلة زمنية (Timeout) كي لا يتجمد النظام
                async with session.get(url, headers=headers, timeout=25) as response:
                    if response.status == 200:
                        content = await response.read()
                        # التأكد من أن الصورة ليست فارغة أو تالفة
                        if len(content) > 15000: 
                            with open(filepath, "wb") as f:
                                f.write(content)
                            return True
                    elif response.status == 429: # Rate limit
                        await asyncio.sleep(2 * (attempt + 1))
            except Exception as e:
                await asyncio.sleep(1)
                
        return False

    async def generate_batch(self, tasks: list) -> dict:
        """
        توليد مجموعة صور في نفس اللحظة.
        تتلقى قائمة من الـ tuples: [(prompt, filename, style), ...]
        """
        results = {}
        # تحديد عدد الاتصالات المتزامنة لكي لا يتم حظرنا من السيرفر (Rate Limiting)
        connector = aiohttp.TCPConnector(limit=5) 
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # إنشاء مهام متزامنة (Coroutines)
            coroutines = []
            for prompt, filename, style in tasks:
                coro = self._fetch_and_save_image(session, prompt, filename, style)
                coroutines.append((filename, coro))
                
            # تشغيل جميع المهام في نفس اللحظة
            for filename, coro in coroutines:
                results[filename] = await coro
                
        return results

# إنشاء نسخة عامة
image_generator = AsyncImageGenerator()

