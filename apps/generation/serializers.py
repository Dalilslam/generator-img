from rest_framework import serializers
from .models import Generation, GenerationImage

class GenerationImageSerializer(serializers.ModelSerializer):
    image_id = serializers.UUIDField(source='id', read_only=True)
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = GenerationImage
        fields = ['image_id', 'url', 'width', 'height']
    
    def get_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.url)
        return obj.url

class GenerationResponseSerializer(serializers.ModelSerializer):
    generated_images = GenerationImageSerializer(source='images', many=True, read_only=True)
    
    class Meta:
        model = Generation
        fields = ['id', 'generated_text', 'generated_images', 'created_at']

class GenerationRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=1000)
    product_images = serializers.ListField(
        child=serializers.ImageField(),
        max_length=5,
        required=False
    )
    
    def validate_prompt(self, value):
        if len(value) > 1000:
            raise serializers.ValidationError("Промпт слишком длинный. Максимум 1000 символов.")
        return value