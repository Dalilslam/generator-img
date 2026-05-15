from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from apps.generation.models import GenerationImage, Generation
from apps.generation.serializers import GenerationResponseSerializer
from apps.auth_app.serializers import ErrorSerializer
from .serializers import ImageListQuerySerializer, ImageDeleteSerializer

class ImagePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 100

class ImageListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = ImagePagination
    
    @extend_schema(
        operation_id="getImages",
        parameters=[
            OpenApiParameter(name='tab', type=str, enum=['generated', 'history', 'favorites', 'archived'], default='history'),
            OpenApiParameter(name='page', type=int, default=1),
            OpenApiParameter(name='limit', type=int, default=20),
        ],
        responses={
            200: GenerationResponseSerializer(many=True),
        },
        tags=['Images (Вкладки изображений)'],
        summary="Список изображений по вкладкам"
    )
    def get(self, request):
        serializer = ImageListQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        tab = serializer.validated_data['tab']
        
        # Базовый queryset
        queryset = Generation.objects.filter(user=request.user, status='completed')
        
        # Фильтрация по вкладкам
        if tab == 'generated':
            from datetime import timedelta
            from django.utils import timezone
            recent_date = timezone.now() - timedelta(days=1)
            queryset = queryset.filter(created_at__gte=recent_date)
        elif tab == 'favorites':
            queryset = queryset.filter(generated_images__is_favorite=True).distinct()
        elif tab == 'archived':
            queryset = queryset.filter(generated_images__is_archived=True).distinct()
        # history - показываем все
        
        # Пагинация
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = GenerationResponseSerializer(
                page, 
                many=True, 
                context={'request': request}
            )
            return paginator.get_paginated_response(serializer.data)
        
        serializer = GenerationResponseSerializer(
            queryset, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        operation_id="deleteImages",
        request=ImageDeleteSerializer,
        responses={
            200: OpenApiResponse(description='Удалено успешно'),
            400: ErrorSerializer,
        },
        tags=['Images (Вкладки изображений)'],
        summary="Удалить выбранные изображения"
    )
    def delete(self, request):
        serializer = ImageDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        image_ids = serializer.validated_data['ids']
        
        deleted_count = GenerationImage.objects.filter(
            id__in=image_ids,
            generation__user=request.user
        ).delete()[0]
        
        return Response(
            {'message': f'Удалено {deleted_count} изображений'},
            status=status.HTTP_200_OK
        )

class ImageFavoriteView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    @extend_schema(
        operation_id="toggleFavorite",
        parameters=[
            OpenApiParameter(name='image_id', type=str, location=OpenApiParameter.PATH, required=True),
        ],
        responses={
            200: OpenApiResponse(description='Статус избранного обновлён'),
            404: ErrorSerializer,
        },
        tags=['Images (Вкладки изображений)'],
        summary="Добавить/убрать из избранного"
    )
    def patch(self, request, image_id):
        try:
            image = GenerationImage.objects.get(
                id=image_id,
                generation__user=request.user
            )
        except GenerationImage.DoesNotExist:
            return Response(
                {'code': 'not_found', 'message': 'Изображение не найдено'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Переключение статуса избранного
        image.is_favorite = not image.is_favorite
        image.save()
        
        return Response({
            'image_id': str(image.id),
            'is_favorite': image.is_favorite
        }, status=status.HTTP_200_OK)