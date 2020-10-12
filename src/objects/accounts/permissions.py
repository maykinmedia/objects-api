from rest_framework.permissions import SAFE_METHODS, BasePermission
from vng_api_common.permissions import bypass_permissions

from objects.accounts.constants import PermissionModes


class ObjectBasedPermission(BasePermission):
    def has_permission(self, request, view):
        if bypass_permissions(request):
            return True

        # user should be authenticated
        if not (request.user and request.user.is_authenticated):
            return False

        # detail actions are processed in has_object_permission method
        if view.action != "create":
            return True

        object_type = request.data["type"]
        object_permission = request.user.get_permission_for_object_type(object_type)
        return bool(
            object_permission
            and object_permission.mode == PermissionModes.read_and_write
        )

    def has_object_permission(self, request, view, obj):
        if bypass_permissions(request):
            return True

        object_permission = request.user.get_permission_for_object_type(obj.object_type)
        if not object_permission:
            return False

        if request.method in SAFE_METHODS:
            return True

        return bool(object_permission.mode == PermissionModes.read_and_write)
