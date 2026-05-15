from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3)
    password = serializers.CharField(min_length=6)

class RegisterRequestSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email')
        extra_kwargs = {
            'username': {'min_length': 3},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class AuthResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    user_id = serializers.UUIDField()
    expires_in = serializers.IntegerField()

class ErrorSerializer(serializers.Serializer):
    code = serializers.CharField()
    message = serializers.CharField()