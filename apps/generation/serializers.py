from rest_framework import serializers
from .models import Generation, GenerationImage

class GenerationImageSerializer(serializers.ModelSerializer):
    image_id = serializers.UUIDField(source='id', read_only=True)
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = GenerationImage
        fields = ['image_id', 'url', 'width', 'height']
    
    def get_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class GenerationResponseSerializer(serializers.ModelSerializer):
    generated_images = GenerationImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Generation
        fields = ['id', 'prompt', 'generated_text', 'generated_images', 'status', 'created_at']

class GenerationRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=1000)
    product_images = serializers.ListField(
        child=serializers.ImageField(),
        max_length=5,
        required=False
    )