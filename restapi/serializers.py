from rest_framework import serializers

from boards.models import Board
from accounts.models import Profile
from pins.models import Pin, Comment


class PinSerializer(serializers.ModelSerializer):
    """
    Used for serializing pin data.
    """

    class Meta:
        model = Pin
        fields = ['pk', 'user', 'title', 'description', 'file', 'get_type']


class ProfileSerializer(serializers.ModelSerializer):
    """
    Used for serializing profile output data.
    """
    user = serializers.SlugRelatedField(slug_field="username", read_only=True, allow_null=True)

    class Meta:
        model = Profile
        fields = ['pk', 'user', 'first_name', 'last_name', 'sex', 'description', 'profile_status', 'photo']


class ProfileEditSerializer(serializers.ModelSerializer):
    """
    Used for serializing profile incoming data.
    """

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'profile_status', 'description', 'sex']


class BoardSerializer(serializers.ModelSerializer):
    """
    Used for serializing board output data.
    """
    user = serializers.SlugRelatedField(slug_field="username", read_only=True, allow_null=True)

    class Meta:
        model = Board
        fields = '__all__'


class BoardCreateSerializer(serializers.ModelSerializer):
    """
    Used for serializing board incoming data.
    """

    class Meta:
        model = Board
        fields = ['title', 'user', 'description', 'is_private', 'cover', 'id']


class CommentSerializer(serializers.ModelSerializer):
    """
    Used for serializing comment output data.
    """

    class Meta:
        model = Comment
        fields = '__all__'


class CommentEditSerializer(serializers.ModelSerializer):
    """
    Used for serializing comment incoming data.
    """

    class Meta:
        model = Comment
        fields = ['text']