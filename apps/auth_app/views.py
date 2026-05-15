from django.contrib.auth import get_user_model
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import (
    LoginRequestSerializer, 
    RegisterRequestSerializer, 
    AuthResponseSerializer,
    ErrorSerializer
)

User = get_user_model()

class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    @extend_schema(
        operation_id="loginUser",
        request=LoginRequestSerializer,
        responses={
            200: AuthResponseSerializer,
            401: ErrorSerializer,
        },
        tags=['Auth'],
        summary="Вход в аккаунт"
    )
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'code': 'invalid_credentials', 'message': 'Неверные учётные данные'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.check_password(password):
            return Response(
                {'code': 'invalid_credentials', 'message': 'Неверные учётные данные'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            'token': str(refresh.access_token),
            'user_id': str(user.id),
            'expires_in': 3600
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    @extend_schema(
        operation_id="registerUser",
        request=RegisterRequestSerializer,
        responses={
            201: AuthResponseSerializer,
            409: ErrorSerializer,
        },
        tags=['Auth'],
        summary="Регистрация нового пользователя"
    )
    def post(self, request):
        serializer = RegisterRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        
        if User.objects.filter(username=username).exists():
            return Response(
                {'code': 'username_exists', 'message': 'Логин уже занят'},
                status=status.HTTP_409_CONFLICT
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {'code': 'email_exists', 'message': 'Email уже используется'},
                status=status.HTTP_409_CONFLICT
            )
        
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            'token': str(refresh.access_token),
            'user_id': str(user.id),
            'expires_in': 3600
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)

class LogoutView(APIView):
    @extend_schema(
        operation_id="logoutUser",
        responses={
            200: OpenApiResponse(description='Сеанс завершён'),
            401: ErrorSerializer,
        },
        tags=['Auth'],
        summary="Выход из профиля"
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response(
                {'message': 'Сеанс завершён'}, 
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {'code': 'token_error', 'message': 'Ошибка токена'},
                status=status.HTTP_401_UNAUTHORIZED
            )