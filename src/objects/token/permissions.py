from rest_framework.permissions import SAFE_METHODS, BasePermission
from vng_api_common.permissions import bypass_permissions

from objects.core.models import ObjectType
from objects.token.constants import PermissionModes


class ObjectTypeBasedPermission(BasePermission):
    def has_permission(self, request, view):
        if bypass_permissions(request):
            return True

        # request should be token authenticated
        if not request.auth:
            return False

        # detail actions are processed in has_object_permission method
        if view.action != "create":
            return True

        object_type_url = request.data["type"]
        try:
            object_type = ObjectType.objects.get_by_url(object_type_url)
        except (ObjectType.DoesNotExist, ValueError, TypeError):
            return False

        object_type_permission = request.auth.get_permission_for_object_type(
            object_type
        )
        return bool(
            object_type_permission
            and object_type_permission.mode == PermissionModes.read_and_write
        )

    def has_object_permission(self, request, view, obj):
        if bypass_permissions(request):
            return True

        object_permission = request.auth.get_permission_for_object_type(obj.object_type)
        if not object_permission:
            return False

        if request.method in SAFE_METHODS:
            return True

        return bool(object_permission.mode == PermissionModes.read_and_write)
