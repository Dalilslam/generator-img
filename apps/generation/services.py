import requests
import random
import time
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from .models import Generation, GenerationImage

class AIGenerationService:
    """
    Гибридный сервис генерации:
    1. Пробует Hugging Face
    2. Если не работает - использует Pollinations.ai
    3. В крайнем случае - создает заглушки
    """
    
    def __init__(self):
        self.hf_headers = {
            "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        self.use_huggingface = True  # Можно переключить на False для тестирования
    
    def generate_text(self, prompt):
        """Генерация рекламного текста"""
        # Пробуем Hugging Face
        if self.use_huggingface:
            try:
                text = self._generate_text_hf(prompt)
                if text and len(text) > 50:
                    return text
            except Exception as e:
                print(f"Hugging Face text failed: {e}")
        
        # Пробуем Pollinations.ai
        try:
            text = self._generate_text_pollinations(prompt)
            if text and len(text) > 50:
                return text
        except Exception as e:
            print(f"Pollinations text failed: {e}")
        
        # Fallback шаблоны
        return self._generate_template_text(prompt)
    
    def _generate_text_hf(self, prompt):
        """Генерация текста через Hugging Face"""
        text_prompt = (
            f"Create a professional advertising text in Russian for a marketplace. "
            f"Product: {prompt}. "
            f"Include: headline, key benefits (3-5 points), call to action with discount."
        )
        
        response = requests.post(
            "https://api-inference.huggingface.co/models/google/flan-t5-large",
            headers=self.hf_headers,
            json={
                "inputs": text_prompt,
                "parameters": {
                    "max_length": 500,
                    "temperature": 0.7,
                    "do_sample": True
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
        
        return None
    
    def _generate_text_pollinations(self, prompt):
        """Генерация текста через Pollinations.ai"""
        text_prompt = f"Создай продающий рекламный текст для маркетплейса на русском языке. Товар: {prompt}"
        
        response = requests.post(
            'https://text.pollinations.ai/',
            json={
                "messages": [{"role": "user", "content": text_prompt}],
                "model": "openai",
                "seed": random.randint(1, 10000)
            },
            timeout=15
        )
        
        if response.status_code == 200:
            return response.text.strip()
        
        return None
    
    def _generate_template_text(self, prompt):
        """Запасной генератор текста"""
        templates = [
            f"""🔥 ХИТ ПРОДАЖ!

{prompt}

✨ ПОЧЕМУ ВЫБИРАЮТ НАС:
• Премиальное качество материалов
• Быстрая доставка по всей России
• Гарантия возврата 30 дней
• Профессиональная поддержка 24/7

💰 СПЕЦИАЛЬНОЕ ПРЕДЛОЖЕНИЕ:
Только сегодня скидка 30% + бесплатная доставка!

🚀 Закажите сейчас и получите подарок!""",
            
            f"""⭐ ВЫБОР ПОКУПАТЕЛЕЙ 2024

{prompt}

🎯 КЛЮЧЕВЫЕ ПРЕИМУЩЕСТВА:
• Инновационный дизайн и эргономика
• Высокая производительность
• Экономия времени и денег
• Экологически чистые материалы

💫 АКЦИЯ ДНЯ:
Купите сегодня со скидкой 25%
+ расширенная гарантия 2 года в подарок!

⚡ Количество ограничено!""",
            
            f"""💎 ПРЕМИУМ КАЧЕСТВО

{prompt}

📊 ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ:
• Современные технологии производства
• Соответствие мировым стандартам
• Многофункциональность и практичность
• Долговечность и надежность

🎁 ВЫГОДНОЕ ПРЕДЛОЖЕНИЕ:
Специальная цена при заказе комплекта
Экономия до 40%!

🎯 Не упустите свой шанс!"""
        ]
        return random.choice(templates)
    
    def generate_images(self, generation, count=4):
        """Генерация изображений"""
        images = []
        
        for i in range(count):
            image = None
            
            # 1. Пробуем Hugging Face
            if self.use_huggingface:
                try:
                    image = self._generate_image_hf(generation, i)
                    if image:
                        images.append(image)
                        print(f"✓ Image {i+1} generated via Hugging Face")
                        continue
                except Exception as e:
                    print(f"Hugging Face image {i+1} failed: {e}")
            
            # 2. Пробуем Pollinations.ai
            try:
                image = self._generate_image_pollinations(generation, i)
                if image:
                    images.append(image)
                    print(f"✓ Image {i+1} generated via Pollinations")
                    continue
            except Exception as e:
                print(f"Pollinations image {i+1} failed: {e}")
            
            # 3. Создаем заглушку
            image = self._create_placeholder(generation, i)
            images.append(image)
            print(f"✓ Image {i+1} placeholder created")
        
        return images
    
    def _generate_image_hf(self, generation, index):
        """Генерация изображения через Hugging Face"""
        prompts = [
            f"{generation.prompt}, front view, product photography, studio lighting, white background, professional, 8k",
            f"{generation.prompt}, angle view, showing features, commercial photography, clean background",
            f"{generation.prompt}, lifestyle photography, product in use, modern interior, natural lighting",
            f"{generation.prompt}, close-up detail shot, macro photography, texture, premium quality"
        ]
        
        response = requests.post(
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
            headers=self.hf_headers,
            json={
                "inputs": prompts[index],
                "parameters": {
                    "negative_prompt": "blurry, low quality, distorted, ugly, bad anatomy, watermark, text",
                    "num_inference_steps": 25,
                    "guidance_scale": 7.5,
                    "width": 1024,
                    "height": 1024
                }
            },
            timeout=60
        )
        
        if response.status_code == 200 and len(response.content) > 1000:
            return self._save_image(generation, response.content, index, "hf")
        
        # Если модель загружается
        if response.status_code == 503:
            print(f"HF model loading for image {index+1}, waiting...")
            time.sleep(10)
            return None
        
        return None
    
    def _generate_image_pollinations(self, generation, index):
        """Генерация изображения через Pollinations.ai"""
        prompts = [
            f"{generation.prompt}, front view, product photography, studio lighting, white background",
            f"{generation.prompt}, side angle, showing details, professional photography",
            f"{generation.prompt}, lifestyle shot, modern setting, natural light",
            f"{generation.prompt}, close-up detail, macro, texture"
        ]
        
        styles = [
            "professional product photography, clean, minimal",
            "e-commerce style, white background, studio lighting",
            "lifestyle photography, modern, bright",
            "detailed macro shot, premium, luxurious"
        ]
        
        import urllib.parse
        full_prompt = f"{prompts[index]}, {styles[index]}"
        encoded_prompt = urllib.parse.quote(full_prompt)
        
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={random.randint(1, 100000)}"
        
        response = requests.get(image_url, timeout=30)
        
        if response.status_code == 200 and len(response.content) > 1000:
            return self._save_image(generation, response.content, index, "pollinations")
        
        return None
    
    def _save_image(self, generation, image_content, index, source):
        """Сохраняет изображение в базу данных"""
        image = GenerationImage.objects.create(
            generation=generation,
            width=1024,
            height=1024
        )
        
        image_name = f"{source}_generated_{generation.id}_{index+1}.png"
        image.image.save(
            image_name,
            ContentFile(image_content),
            save=True
        )
        
        return image
    
    def _create_placeholder(self, generation, index):
        """Создает красивое placeholder изображение"""
        color_schemes = [
            [(99, 102, 241), (139, 92, 246)],    # Purple
            [(59, 130, 246), (147, 197, 253)],    # Blue
            [(236, 72, 153), (244, 114, 182)],    # Pink
            [(16, 185, 129), (110, 231, 183)],    # Green
        ]
        
        titles = ["ОСНОВНОЙ ВИД", "РАКУРС СБОКУ", "В ИСПОЛЬЗОВАНИИ", "ДЕТАЛИ"]
        icons = ["📦", "📸", "✨", "🔍"]
        
        color1, color2 = color_schemes[index]
        
        # Создаем изображение
        img = Image.new('RGB', (1024, 1024), color1)
        draw = ImageDraw.Draw(img)
        
        # Градиентный фон
        for y in range(1024):
            r = int(color1[0] + (color2[0] - color1[0]) * y / 1024)
            g = int(color1[1] + (color2[1] - color1[1]) * y / 1024)
            b = int(color1[2] + (color2[2] - color1[2]) * y / 1024)
            draw.line([(0, y), (1024, y)], fill=(r, g, b))
        
        # Белая рамка
        margin = 40
        draw.rectangle(
            [margin, margin, 1024-margin, 1024-margin],
            outline=(255, 255, 255, 180),
            width=4
        )
        
        # Добавляем элементы дизайна
        try:
            font_large = ImageFont.truetype("arial.ttf", 150)
            font_title = ImageFont.truetype("arial.ttf", 50)
            font_text = ImageFont.truetype("arial.ttf", 30)
        except:
            font_large = ImageFont.load_default()
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
        
        # Иконка
        draw.text((387, 250), icons[index], font=font_large, fill=(255, 255, 255))
        
        # Заголовок
        title = titles[index]
        bbox = draw.textbbox((0, 0), title, font=font_title)
        title_width = bbox[2] - bbox[0]
        draw.text(((1024-title_width)/2, 480), title, font=font_title, fill=(255, 255, 255))
        
        # Описание товара
        product_text = generation.prompt[:50]
        if len(product_text) > 40:
            product_text = product_text[:40] + "..."
        
        bbox = draw.textbbox((0, 0), product_text, font=font_text)
        text_width = bbox[2] - bbox[0]
        draw.text(((1024-text_width)/2, 600), product_text, font=font_text, fill=(255, 255, 255, 200))
        
        # Декоративные круги
        for i in range(3):
            x = 200 + i * 300
            y = 750
            draw.ellipse([x-30, y-30, x+30, y+30], outline=(255, 255, 255, 100), width=2)
        
        # Сохраняем
        img_io = BytesIO()
        img.save(img_io, format='PNG', quality=95)
        img_io.seek(0)
        
        # Создаем запись в БД
        image = GenerationImage.objects.create(
            generation=generation,
            width=1024,
            height=1024
        )
        
        image.image.save(
            f"placeholder_{generation.id}_{index+1}.png",
            ContentFile(img_io.read()),
            save=True
        )
        
        return image
    
    def process_generation(self, generation):
        """Основной метод обработки генерации"""
        try:
            print("\n" + "="*50)
            print(f"Starting generation for: {generation.prompt[:50]}")
            print("="*50 + "\n")
            
            # Генерация текста
            print("📝 Generating text...")
            generation.generated_text = self.generate_text(generation.prompt)
            generation.status = 'processing'
            generation.save()
            print("✓ Text generated\n")
            
            # Генерация изображений
            print("🖼️  Generating images...")
            self.generate_images(generation)
            print("\n✓ Images generated\n")
            
            generation.status = 'completed'
            generation.save()
            
            print("="*50)
            print("✓ Generation completed!")
            print("="*50 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Generation error: {e}")
            import traceback
            traceback.print_exc()
            
            generation.status = 'failed'
            generation.generated_text = f"Ошибка генерации: {str(e)}"
            generation.save()
            return False