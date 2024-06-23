"""
Tests for blogCreator APIs
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Blog

from blogcreator.serializers import BlogSerializer


BLOGS_URL = reverse("blogcreator:blog-list")


def create_blog(user, **params):
    """Create and return a blog"""

    defaults = {
        "title": "Blog Title",
        "caption": "Blog caption",
        "url": "http://example.com/image.png",
        "time_minutes": 5,
    }
    defaults.update(params)
    blog = Blog.objects.create(user=user, **defaults)

    return blog


class PublicBlogAPITest(TestCase):
    """Test unathenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(BLOGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBlogApiTests(TestCase):
    """Test authenticate API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "testuser@test.com", "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_blogs(self):
        """Test retrieving a list of blogs"""
        create_blog(user=self.user)
        create_blog(user=self.user)

        res = self.client.get(BLOGS_URL)

        blogs = Blog.objects.all().order_by("-id")
        serializer = BlogSerializer(blogs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_blog_limited_to_authentication(self):
        """Test list of blogs is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            "otheruser@other.com", "otherpass123"
        )
        create_blog(user=other_user)
        create_blog(user=self.user)

        res = self.client.get(BLOGS_URL)

        blogs = Blog.objects.filter(user=self.user)
        serializer = BlogSerializer(blogs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
