from django.db import models
from django.contrib.auth.models import User

# Create your models here.

STATUS_CHOICES = (
    ("Active", "Active"),
    ("Inactive" , "Inactive")
)

class OauthModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="oauth_tokens", blank=True, null=True)
    connection_name = models.CharField(max_length=255, blank=True, null=True)
    orgId = models.CharField(max_length=200, blank=True, null=True)
    client_id = models.CharField(max_length=200, blank=True, null=True)
    secret_id = models.CharField(max_length=200, blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default="Active")
    create_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.email}'
    
class NMGDepartmentModel(models.Model):
    oauthModal = models.ForeignKey(OauthModel, on_delete=models.CASCADE, related_name="NMGDepartmentModel", blank=False, null=False)
    departmentid = models.CharField(max_length=200, blank=False, null=False)
    depatment_name = models.CharField(max_length=200, blank=False, null=False)
    create_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

class ZenDepartmentModel(models.Model):
    oauthModal = models.ForeignKey(OauthModel, on_delete=models.CASCADE, related_name="ZenDepartmentModel", blank=False, null=False)
    departmentid = models.CharField(max_length=200, blank=False, null=False)
    depatment_name = models.CharField(max_length=200, blank=False, null=False)
    create_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

class CsvSchedule(models.Model):
    oauthModal = models.ForeignKey(OauthModel, on_delete=models.CASCADE, related_name="CsvSchedule", blank=False, null=False)
    name = models.CharField(max_length=100, unique=True)
    last_row = models.PositiveIntegerField(default=0)
    last_run = models.DateTimeField(null=True, blank=True)
    is_running = models.BooleanField(default=False)
