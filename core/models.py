# core/models.py
from django.db import models
from django.conf import settings

class Company(models.Model):
    name = models.CharField(max_length=255)
    plan = models.CharField(max_length=50, default="basic")
    end_date = models.DateField(null=True, blank=True)


settings.AUTH_USER_MODEL
on_delete=models.CASCADE,
related_name='owned_company',  # مهم عشان ميحصلش clash
null=True,
blank=True
    

def __str__(self):
        return self.name

class Branch(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='branches')

    def __str__(self):
        return f"{self.name} - {self.company.name}"
