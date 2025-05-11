from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenVerifySerializer
from django.contrib.auth import get_user_model
from accounts.models import User 

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "password", "phone", "role"]
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.full_clean()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.full_clean()
        instance.save()
        return instance
class CustomLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email and password are required")

        user = get_user_model().objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        attrs["user"] = user
        return attrs
    

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = serializers.CharField(required=True)

    def validate(self, attrs):
        return super().validate(attrs)


class CustomTokenVerifySerializer(TokenVerifySerializer):
    token = serializers.CharField(required=True)

    def validate(self, attrs):
        return super().validate(attrs)