from django.db.models import Sum
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import AnalyticsData
from .serializers import AnalyticsResponseSerializer, AnalyticsRequestSerializer
from apps.auth_app.serializers import ErrorSerializer

class AnalyticsMetricsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    @extend_schema(
        operation_id="getAnalyticsMetrics",
        parameters=[
            OpenApiParameter(name='start_date', type=str, required=True, description='Начальная дата'),
            OpenApiParameter(name='end_date', type=str, required=True, description='Конечная дата'),
            OpenApiParameter(name='granularity', type=str, enum=['day', 'week', 'month'], default='day'),
        ],
        responses={
            200: AnalyticsResponseSerializer,
            400: ErrorSerializer,
        },
        tags=['Analytics (Графики)'],
        summary="Данные для окна графиков",
        description="Возвращает метрики и временные ряды для построения графиков"
    )
    def get(self, request):
        request_serializer = AnalyticsRequestSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)
        
        start_date = request_serializer.validated_data['start_date']
        end_date = request_serializer.validated_data['end_date']
        granularity = request_serializer.validated_data['granularity']
        
        queryset = AnalyticsData.objects.filter(
            generation__user=request.user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        summary = queryset.aggregate(
            total_views=Sum('views'),
            total_clicks=Sum('clicks'),
            conversions=Sum('conversions')
        )
        
        total_views = summary['total_views'] or 0
        total_clicks = summary['total_clicks'] or 0
        ctr = (total_clicks / total_views * 100) if total_views > 0 else 0.0
        
        if granularity == 'week':
            trunc_func = TruncWeek
        elif granularity == 'month':
            trunc_func = TruncMonth
        else:
            trunc_func = TruncDate
        
        timeseries = queryset.annotate(
            period=trunc_func('date')
        ).values('period').annotate(
            views=Sum('views'),
            clicks=Sum('clicks')
        ).order_by('period')
        
        timeseries_data = []
        for item in timeseries:
            item_views = item['views'] or 0
            item_clicks = item['clicks'] or 0
            item_ctr = (item_clicks / item_views * 100) if item_views > 0 else 0.0
            
            timeseries_data.append({
                'date': item['period'],
                'views': item_views,
                'clicks': item_clicks,
                'ctr': round(item_ctr, 2)
            })
        
        response_data = {
            'summary': {
                'total_views': total_views,
                'total_clicks': total_clicks,
                'ctr': round(ctr, 2),
                'conversions': summary['conversions'] or 0
            },
            'timeseries': timeseries_data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)