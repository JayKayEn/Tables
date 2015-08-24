from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Person, Table, Followees

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ('id', 'profile', 'user_id', 'username', 'profile_picture_url', 'full_name', )

class TableSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all(), required=False, allow_null=True, default=None)
    people = serializers.SlugRelatedField(many=True, read_only=True, slug_field='username')

    class Meta:
        model = Table
        fields = ('id', 'user', 'name', 'people', )


class FolloweesSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all(), required=False, allow_null=True, default=None)
    people = serializers.SlugRelatedField(many=True, read_only=True, slug_field='username')

    class Meta:
        model = Followees
        fields = ('id', 'user', 'people', )
