from django.db import models

import uuid

# Create your models here.

class Item(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default='dummy-item', blank=True)

    def __str__(self):
        return self.name