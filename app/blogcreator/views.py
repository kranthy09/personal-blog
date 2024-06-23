"""
Views for the recipe APIs.
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Blog
from blogcreator import serializers


class BlogViewSet(viewsets.ModelViewSet):
    """View for manage Blog APIs."""

    serializer_class = serializers.BlogSerializer
    queryset = Blog.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieves blogs for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by(
            "-created_at"
        )
