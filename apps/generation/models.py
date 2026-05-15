import uuid
from django.db import models
from django.conf import settings

class Generation(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='generations')
    prompt = models.TextField()
    generated_text = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'generations'
        verbose_name = 'Генерация'
        verbose_name_plural = 'Генерации'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Generation {self.id} - {self.prompt[:50]}"

class GenerationImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='generated_images/')
    width = models.IntegerField(default=1024)
    height = models.IntegerField(default=1024)
    is_favorite = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'generation_images'
        verbose_name = 'Изображение генерации'
        verbose_name_plural = 'Изображения генераций'
    
    def __str__(self):
        return f"Image {self.id} for Generation {self.generation.id}"
    
    @property
    def url(self):
        if self.image:
            return self.image.url
        return None

class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_images'
        verbose_name = 'Фото товара'
        verbose_name_plural = 'Фото товаров'
    
    def __str__(self):
        return f"Product Image {self.id}"