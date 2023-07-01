from rest_framework import serializers

class UserSigninSerializer(serializers.Serializer):
    username = serializers.CharField(required = True)
    password = serializers.CharField(required = True)

class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()