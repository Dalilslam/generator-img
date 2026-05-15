# Модели уже определены в apps/generation/models.py
# Здесь мы создадим дополнительные методы и менеджеры

from django.db import models
from apps.generation.models import GenerationImage

class ImageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
    
    def by_tab(self, tab):
        """Фильтрация по вкладкам"""
        if tab == 'generated':
            return self.filter(is_archived=False, is_favorite=False)
        elif tab == 'favorites':
            return self.filter(is_favorite=True)
        elif tab == 'archived':
            return self.filter(is_archived=True)
        else:  # history - все изображения
            return self.all()
    
    def for_user(self, user):
        """Изображения конкретного пользователя"""
        return self.filter(generation__user=user)

# Добавляем менеджер к существующей модели
GenerationImage.add_to_class('objects', ImageManager())