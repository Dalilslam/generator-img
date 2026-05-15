import os
import django
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_generator.settings')
django.setup()

from apps.auth_app.models import User
from apps.generation.models import Generation, GenerationImage
from apps.analytics.models import AnalyticsData

def create_test_data():
    # Получаем или создаем тестового пользователя
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'is_active': True
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Создан пользователь: {user.username}")
    
    # Создаем несколько генераций
    prompts = [
        "Смарт-часы на сером фоне, спортивный стиль, акцент на автономность",
        "Кроссовки для бега, динамичный стиль, яркие цвета",
        "Наушники беспроводные, минималистичный дизайн, акцент на качество звука",
        "Крем для лица, натуральные компоненты, свежесть и уход",
        "Электросамокат, городской стиль, экологичность и скорость"
    ]
    
    for i, prompt in enumerate(prompts):
        generation = Generation.objects.create(
            user=user,
            prompt=prompt,
            generated_text=f"Рекламный текст для: {prompt}. Уникальное предложение! Скидка {random.randint(10, 50)}% только сегодня!",
            status='completed',
            created_at=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        
        # Создаем 4 изображения для каждой генерации
        for j in range(4):
            GenerationImage.objects.create(
                generation=generation,
                width=1024,
                height=1024,
                is_favorite=random.choice([True, False]),
                created_at=generation.created_at
            )
        
        # Создаем аналитику за последние 30 дней
        for day in range(30):
            date = datetime.now().date() - timedelta(days=day)
            AnalyticsData.objects.create(
                generation=generation,
                views=random.randint(100, 1000),
                clicks=random.randint(10, 100),
                conversions=random.randint(0, 10),
                date=date
            )
        
        print(f"Создана генерация {i+1}/5: {prompt[:50]}...")
    
    print("\n✓ Тестовые данные успешно созданы!")
    print(f"  - Пользователь: testuser / testpass123")
    print(f"  - Сгенерировано: 5 рекламных комплектов")
    print(f"  - Аналитика: за 30 дней")

if __name__ == '__main__':
    create_test_data()