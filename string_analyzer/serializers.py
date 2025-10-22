from rest_framework import serializers
from .models import StoredString


class PropertiesSerializer(serializers.Serializer):
    length = serializers.IntegerField()
    is_palindrome = serializers.BooleanField()
    unique_characters = serializers.IntegerField()
    word_count = serializers.IntegerField()
    sha256_hash = serializers.CharField()
    character_frequency_map = serializers.DictField(child=serializers.IntegerField())


class StoredStringSerializer(serializers.ModelSerializer):
    properties = serializers.JSONField()
    class Meta:
        model = StoredString
        fields = ['id', 'value', 'properties', 'created_at']


class CreateStringSerializer(serializers.Serializer):
    value = serializers.CharField()
    def validate_value(self, v):
        if not isinstance(v, str):
            raise serializers.ValidationError('value must be a string')
        return v
