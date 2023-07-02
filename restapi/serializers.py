from rest_framework import serializers

from boards.models import Board
from accounts.models import Profile
from pins.models import Pin


class PinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pin
        fields = ['pk', 'user', 'title', 'description', 'file', 'get_type']


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True, allow_null=True)

    class Meta:
        model = Profile
        fields = ['pk', 'user', 'first_name', 'last_name', 'sex', 'description', 'profile_status', 'photo']


class ProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'profile_status', 'description', 'sex']


class BoardSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True, allow_null=True)
    class Meta:
        model = Board
        fields = '__all__'


class BoardCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Board
        fields = ['title', 'user', 'description', 'is_private', 'cover', 'id']