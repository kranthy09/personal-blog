"""
Tests for models
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful"""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.com", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]
        for email, expected_email in sample_emails:
            user = get_user_model().objects.create_user(email, "testpass123")
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raised_error(self):
        """Test that creating a new user without an email raises"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "testpass123")

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            "test@example.com", "testpass123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_blog(self):
        """Test creating a blog is successful"""
        user = get_user_model().objects.create_user(
            "test@example.com", "testpass123"
        )
        blog = models.Blog.objects.create(
            user=user,
            title="Test Blog",
            caption="Test caption",
            url="http://example.com/image.png",
            time_minutes=5,
        )
        self.assertEqual(blog.title, "Test Blog")
        self.assertEqual(blog.caption, "Test caption")
        self.assertEqual(blog.url, "http://example.com/image.png")
        self.assertEqual(blog.time_minutes, 5)
        self.assertEqual(blog.user, user)
