"""
Tests for blogCreator APIs
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Blog

from blogcreator.serializers import BlogSerializer, BlogDetailSerializer


BLOGS_URL = reverse("blogcreator:blog-list")


def detail_url(blog_id):
    """Create and return a blog detail URL"""
    return reverse("blogcreator:blog-detail", args=[blog_id])


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


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(
            email="testuser@test.com",
            password="testpass123",
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
        other_user = create_user(
            email="otheruser@other.com",
            password="otherpass123",
        )
        create_blog(user=other_user)
        create_blog(user=self.user)

        res = self.client.get(BLOGS_URL)

        blogs = Blog.objects.filter(user=self.user)
        serializer = BlogSerializer(blogs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_get_blog_detail(self):
        """Test get blog detail"""
        blog = create_blog(user=self.user)
        url = detail_url(blog.id)
        res = self.client.get(url)
        serializer = BlogDetailSerializer(blog)
        self.assertEqual(res.data, serializer.data)

    def test_create_blog_successful(self):
        """Test creating a blog"""
        payload = {
            "title": "Blog Title",
            "caption": "Blog caption",
            "url": "http://example.com/image.png",
            "time_minutes": 5,
        }
        res = self.client.post(BLOGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        blog = Blog.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(blog, k), v)
        self.assertEqual(blog.user, self.user)

    def test_partial_update(self):
        """Test partial update of a blog."""
        original_link = "http://image.png"
        blog = create_blog(
            user=self.user,
            title="Sample blog title",
            url=original_link,
        )
        payload = {
            "title": "New blog title",
        }
        url = detail_url(blog.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        blog.refresh_from_db()
        self.assertEqual(blog.title, payload["title"])
        self.assertEqual(blog.url, original_link)
        self.assertEqual(blog.user, self.user)

    def test_full_update(self):
        """Test full update of blog"""
        blog = create_blog(
            user=self.user,
            title="Sample blog title",
            url="http://image.png",
        )
        payload = {
            "title": "New blog title",
            "caption": "New blog caption",
            "url": "http://newimage.png",
            "time_minutes": 10,
        }
        url = detail_url(blog.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        blog.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(blog, k), v)
        self.assertEqual(blog.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the blog user results in an error"""
        new_user = create_user(
            email="user2@example.com",
            password="password123",
        )
        blog = create_blog(
            user=self.user,
            title="Sample blog title",
            url="http://image.png",
        )
        payload = {
            "user": new_user.id,
        }
        url = detail_url(blog.id)
        self.client.patch(url, payload)
        blog.refresh_from_db()
        self.assertEqual(blog.user, self.user)

    def test_delete_blog(self):
        """Test deleting a blog successful"""
        blog = create_blog(user=self.user)
        url = detail_url(blog.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Blog.objects.filter(id=blog.id).exists())

    def test_delete_other_users_blog_error(self):
        """Test trying to delete anther users recipe gives error"""
        new_user = create_user(
            email="user2@example.com",
            password="password123",
        )
        blog = create_blog(user=new_user)
        url = detail_url(blog.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Blog.objects.filter(id=blog.id).exists())
