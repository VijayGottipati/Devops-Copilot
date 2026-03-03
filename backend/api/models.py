from django.db import models
from cryptography.fernet import Fernet
from pgvector.django import VectorField
import os

def get_fernet():
    key = os.environ.get('TOKEN_ENCRYPTION_KEY')
    if not key:
        raise ValueError("TOKEN_ENCRYPTION_KEY is not set in environment.")
    return Fernet(key.encode())

class EncryptedTextField(models.TextField):
    """A custom text field that encrypts data at rest using Fernet."""
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return get_fernet().decrypt(value.encode()).decode()
        except:
            return value

    def get_prep_value(self, value):
        if value is None:
            return value
        return get_fernet().encrypt(value.encode()).decode()

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Teammate(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='teammates')
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=100, blank=True)
    slack_id = models.CharField(max_length=100, blank=True, null=True)
    discord_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class AutomationRule(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='rules')
    trigger_keyword = models.CharField(max_length=255)
    action_type = models.CharField(max_length=100) # e.g., 'auto_reply', 'alert'
    priority = models.CharField(max_length=50, default='neutral')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.action_type} on {self.trigger_keyword}"

class AgentMemory(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memories')
    content = models.TextField()
    embedding = VectorField(dimensions=768) # 768 for Gemini standard vector models
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Memory for {self.project.name} at {self.created_at}"

class OAuthToken(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tokens')
    provider = models.CharField(max_length=50) # 'slack', 'discord', 'gmail', 'github'
    access_token = EncryptedTextField()
    refresh_token = EncryptedTextField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project', 'provider')

    def __str__(self):
        return f"{self.provider} token for {self.project.name}"
