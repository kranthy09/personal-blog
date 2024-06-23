"""
Serializers for blog apis
"""

from rest_framework import serializers

from core.models import Blog


class BlogSerializer(serializers.ModelSerializer):
    """Serializer for blog"""

    class Meta:
        model = Blog
        fields = (
            "id",
            "title",
            "caption",
            "url",
            "time_minutes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
