from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from adminclient import models
from adminclient.models import PermissionsInstance
from django.contrib.contenttypes.models import ContentType

def add_role_permissions():
    owner = Group.objects.create(name='Owner')
    admin = Group.objects.create(name='Admin')
    foreigner = Group.objects.create(name='Foreigner')
    content_type = ContentType.objects.get_for_model(PermissionsInstance)
    post_permission = Permission.objects.filter(content_type=content_type)

    for perm in post_permission:
        if perm.codename == "can_see_view":
            owner.permissions.add(perm)
            admin.permissions.add(perm)

        elif perm.codename == "can_edit_view":
            owner.permissions.add(perm)
            admin.permissions.add(perm)

add_role_permissions()