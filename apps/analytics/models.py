import uuid
from django.db import models
from django.conf import settings
from apps.generation.models import Generation

class AnalyticsData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE, related_name='analytics')
    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_data'
        verbose_name = 'Аналитические данные'
        verbose_name_plural = 'Аналитические данные'
        unique_together = ['generation', 'date']
    
    @property
    def ctr(self):
        """Click-Through Rate"""
        if self.views > 0:
            return (self.clicks / self.views) * 100
        return 0.0
    
    def __str__(self):
        return f"Analytics for {self.generation.id} on {self.date}"