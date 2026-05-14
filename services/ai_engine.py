# services/ai_engine.py
import os
import json
import random
import time
import google.generativeai as genai
from typing import Dict, Any

class KeyManager:
    """مدير المفاتيح الذكي: يدور بين المفاتيح المتاحة ويتجاوز المحظورة تلقائياً"""
    def __init__(self):
        self.keys = self._load_keys()
    
    def _load_keys(self) -> list:
        keys = []
        for i in range(1, 6):
            key = os.getenv(f"GEMINI_API_KEY_{i}", "").strip()
            if key:
                keys.append(key)
        
        default_key = os.getenv("GEMINI_API_KEY", "").strip()
        if default_key and default_key not in keys:
            keys.append(default_key)
            
        return keys if keys else ["DUMMY_KEY"]

    def get_random_key(self) -> str:
        if not self.keys or self.keys[0] == "DUMMY_KEY":
            raise ValueError("لا توجد مفاتيح API صالحة. يرجى إعداد GEMINI_API_KEY.")
        return random.choice(self.keys)

    def remove_key(self, key: str):
        if key in self.keys:
            self.keys.remove(key)

class AIEngine:
    """عقل المصنع: يتواصل مع Gemini ويضمن عودة البيانات بهيكل JSON دقيق"""
    def __init__(self):
        self.key_manager = KeyManager()
        self.max_retries = 3

    def _generate_json(self, prompt: str, fallback_data: Dict[str, Any]) -> Dict[str, Any]:
        """دالة أساسية تضمن الحصول على JSON صالح مهما حدث"""
        for attempt in range(self.max_retries):
            current_key = self.key_manager.get_random_key()
            try:
                genai.configure(api_key=current_key)
                
                # إعداد النموذج لإرجاع JSON حصراً
                model = genai.GenerativeModel(
                    'gemini-1.5-flash',
                    generation_config={
                        "temperature": 0.7,
                        "response_mime_type": "application/json"
                    }
                )
                
                response = model.generate_content(prompt)
                
                if response and response.text:
                    # تحويل النص العائد إلى كائن بايثون (Dictionary)
                    return json.loads(response.text)

            except json.JSONDecodeError:
                # إذا لم يكن العائد JSON صالحاً، نعيد المحاولة
                time.sleep(1)
                continue
            except Exception as e:
                error_str = str(e)
                if "403" in error_str or "API_KEY_INVALID" in error_str:
                    self.key_manager.remove_key(current_key) # حذف المفتاح التالف
                time.sleep(2)
                continue
                
        return fallback_data # في أسوأ الحالات نعيد بيانات افتراضية لكي لا يتوقف النظام

    def parse_open_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """تحليل الموجه المفتوح بدقة عالية"""
        prompt = f"""
        Analyze this user request for creating a book: "{user_prompt}"
        
        Extract the details and return ONLY a valid JSON object with these exact keys:
        - "theme": The main topic in Arabic (max 50 chars).
        - "pages": Integer between 10 and 100.
        - "mode": Must be exactly one of: ["تلوين للأطفال", "قصص مصورة", "ألغاز ونشاطات", "مخططات ودفاتر", "بطاقات تعليمية", "تشكيلة منوعة"].
        - "enhanced_idea": A more creative, descriptive version of the theme in Arabic.
        """
        
        fallback = {
            "theme": "كتاب إبداعي",
            "pages": 24,
            "mode": "تشكيلة منوعة",
            "enhanced_idea": "كتاب إبداعي شامل للأطفال"
        }
        
        return self._generate_json(prompt, fallback)

    def generate_marketing(self, theme: str) -> Dict[str, Any]:
        """توليد حزمة تسويقية متكاملة لمنصات البيع"""
        prompt = f"""
        Act as an expert KDP and Etsy seller. Create a launch package for a book about: '{theme}'
        
        Return ONLY a valid JSON object with these exact keys:
        - "seo_title": An SEO-optimized title in English (Title: Subtitle format).
        - "keywords": A string of exactly 7 highly searched tags, comma-separated.
        - "description": A persuasive 3-paragraph product description in English with HTML formatting (<b>, <ul>, etc).
        - "tiktok_script": A short, viral 30-second TikTok voiceover script to sell this book.
        """
        
        fallback = {
            "seo_title": f"Amazing {theme} Book for Kids",
            "keywords": "kids, book, fun, learning, creative, gift, activity",
            "description": f"<p>Discover the magic of <b>{theme}</b> with this amazing book!</p>",
            "tiktok_script": f"Stop scrolling! If your kid loves {theme}, you NEED to see this new book!"
        }
        
        return self._generate_json(prompt, fallback)

    def generate_niche(self) -> str:
        """توليد نيش مربح عشوائي"""
        prompt = """
        Return ONLY a valid JSON object with one key:
        - "niche": A highly profitable, low-competition 2-3 word micro-niche for a KDP or Etsy digital product. Be extremely creative. (e.g., 'Cyberpunk Dinosaurs', 'Zen Mushrooms').
        """
        result = self._generate_json(prompt, {"niche": "Fantasy Animals"})
        return result.get("niche", "Fantasy Animals")

# إنشاء نسخة عامة يمكن استدعاؤها من أي مكان في المشروع
ai_engine = AIEngine()

