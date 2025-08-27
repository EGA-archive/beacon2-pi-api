from django.db import models

# Create your models here.

class PermissionsInstance(models.Model):
    # …
    class Meta:
        # …
        permissions = [("can_edit_view", "can_edit_view"), ("can_see_view", "can_see_view")]