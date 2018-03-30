from django.db.models.signals import pre_delete,post_delete
from django.dispatch import receiver

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from guardian.models import UserObjectPermission
from guardian.models import GroupObjectPermission

@receiver(post_delete)
def remove_obj_perms_connected_with_user(sender, instance, **kwargs):
    '''
    删除完成后，清除该对象关联的对象级别权限，因为对象级别权限依靠
    genericForeignKey，而不是真正的ForeignKey，无法自动级联删除
    '''
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
        object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()

