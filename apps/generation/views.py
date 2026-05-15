from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .models import Generation, ProductImage
from .serializers import GenerationRequestSerializer, GenerationResponseSerializer
from .services import AIGenerationService
from apps.auth_app.serializers import ErrorSerializer

class GenerationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    throttle_scope = 'generation'
    
    @extend_schema(
        operation_id="generateContent",
        request=GenerationRequestSerializer,
        responses={
            200: GenerationResponseSerializer,
            400: ErrorSerializer,
            429: ErrorSerializer,
            500: ErrorSerializer,
        },
        tags=['Generation'],
        summary="Генерация рекламного комплекта",
        description="Принимает промпт и фото товара, возвращает готовый контент."
    )
    def post(self, request):
        serializer = GenerationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Создание записи генерации
        generation = Generation.objects.create(
            user=request.user,
            prompt=serializer.validated_data['prompt'],
            status='processing'
        )
        
        # Сохранение загруженных изображений товара
        if 'product_images' in request.FILES:
            images = request.FILES.getlist('product_images')
            for image in images[:5]:
                ProductImage.objects.create(
                    generation=generation,
                    image=image
                )
        
        # Создаем экземпляр сервиса и запускаем генерацию
        ai_service = AIGenerationService()
        success = ai_service.process_generation(generation)
        
        if not success:
            return Response(
                {'code': 'generation_failed', 'message': 'Ошибка AI-моделей'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Обновляем объект из базы
        generation.refresh_from_db()
        
        # Возвращаем результат
        response_serializer = GenerationResponseSerializer(
            generation, 
            context={'request': request}
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)