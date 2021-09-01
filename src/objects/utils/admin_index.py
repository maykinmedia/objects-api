from django_admin_index.conf import settings


def should_display_dropdown_menu(request):
    # not showing for two_factor views
    return (
        settings.SHOW_MENU
        and request.user.is_authenticated
        and request.user.is_staff
        and request.user.is_verified()
        and request.resolver_match.app_name != "admin:two_factor"
    )
