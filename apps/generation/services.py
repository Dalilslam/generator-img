import random
from .models import Generation, GenerationImage

class AIGenerationService:
    """
    Сервис для генерации рекламного контента с использованием AI.
    В реальном приложении здесь будет интеграция с AI-моделями.
    """
    
    @staticmethod
    def generate_text(prompt):
        """
        Генерация рекламного текста на основе промпта.
        В реальности здесь будет вызов AI-модели.
        """
        # Заглушка для демонстрации
        templates = [
            f"Революционный продукт! {prompt}. Ограниченное предложение!",
            f"Откройте для себя {prompt}. Качество премиум-класса по доступной цене.",
            f"Ваш идеальный выбор: {prompt}. Закажите сейчас и получите скидку 20%!",
            f"Почему тысячи покупателей выбирают {prompt}? Узнайте сами!",
        ]
        return random.choice(templates)
    
    @staticmethod
    def generate_images(generation, count=4):
        """
        Генерация изображений для рекламы.
        В реальности здесь будет вызов AI-модели для генерации изображений.
        """
        # Заглушка - создаем placeholder изображения
        images = []
        for i in range(count):
            image = GenerationImage.objects.create(
                generation=generation,
                width=1024,
                height=1024,
                # В реальности здесь будет сохранение сгенерированного изображения
            )
            images.append(image)
        return images
    
    @staticmethod
    def process_generation(generation):
        """
        Основной метод обработки генерации.
        """
        try:
            # Генерация текста
            generation.generated_text = AIGenerationService.generate_text(generation.prompt)
            
            # Генерация изображений
            AIGenerationService.generate_images(generation)
            
            generation.status = 'completed'
            generation.save()
            
            return True
        except Exception as e:
            generation.status = 'failed'
            generation.save()
            return False