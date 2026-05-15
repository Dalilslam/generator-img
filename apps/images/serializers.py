from rest_framework import serializers

class ImageListQuerySerializer(serializers.Serializer):
    tab = serializers.ChoiceField(
        choices=['generated', 'history', 'favorites', 'archived'],
        default='history'
    )
    page = serializers.IntegerField(default=1, min_value=1)
    limit = serializers.IntegerField(default=20, min_value=1, max_value=100)

class ImageDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100
    )