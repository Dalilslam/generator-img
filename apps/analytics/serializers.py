from rest_framework import serializers
from .models import AnalyticsData
from datetime import datetime

class TimeseriesDataSerializer(serializers.Serializer):
    date = serializers.DateField()
    views = serializers.IntegerField()
    clicks = serializers.IntegerField()
    ctr = serializers.FloatField()

class SummarySerializer(serializers.Serializer):
    total_views = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    ctr = serializers.FloatField()
    conversions = serializers.IntegerField()

class AnalyticsResponseSerializer(serializers.Serializer):
    summary = SummarySerializer()
    timeseries = TimeseriesDataSerializer(many=True)

class AnalyticsRequestSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    granularity = serializers.ChoiceField(
        choices=['day', 'week', 'month'],
        default='day'
    )
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError(
                "start_date должен быть меньше end_date"
            )
        return data