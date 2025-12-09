from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Extends User with resume-relevant fields.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)  # Quick summary for AI personalization

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class Resume(models.Model):
    """
    Stores user resumes with AI-generated sections.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('generated', 'AI Generated'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200, default='My Professional Resume')
    sections = models.JSONField(default=dict)  # e.g., {'experience': [...], 'skills': [...]}
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pdf_url = models.URLField(blank=True, null=True)  # For exported PDF links

    def __str__(self):
        return f"{self.title} by {self.user.username} ({self.status})"

    class Meta:
        ordering = ['-created_at']  # Newest first
        verbose_name = "Resume"
        verbose_name_plural = "Resumes"