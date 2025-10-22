from django.db import models

# Create your models here.


class StoredString(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    value = models.TextField()
    properties = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


def __str__(self):
    return f"StoredString(id={self.id})"