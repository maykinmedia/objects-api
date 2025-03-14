from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic.base import TemplateView

from maykin_2fa import monkeypatch_admin
from maykin_2fa.urls import urlpatterns as maykin_2fa_urlpatterns, webauthn_urlpatterns
from mozilla_django_oidc_db.views import AdminLoginFailure
from rest_framework.settings import api_settings

from objects.accounts.views import QRGeneratorView

handler500 = "objects.utils.views.server_error"
admin.site.site_header = "objects admin"
admin.site.site_title = "objects admin"
admin.site.index_title = "Welcome to the objects admin"
admin.site.enable_nav_sidebar = False

monkeypatch_admin()

urlpatterns = [
    path(
        "admin/password_reset/",
        auth_views.PasswordResetView.as_view(),
        name="admin_password_reset",
    ),
    path(
        "admin/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path("admin/login/failure/", AdminLoginFailure.as_view(), name="admin-oidc-error"),
    # See https://github.com/maykinmedia/open-api-framework/issues/40
    # and https://github.com/maykinmedia/open-api-framework/issues/59
    # Temporary workaround to remove the dependency on `django.contrib.sites` when
    # generating the app label for 2FA. This should be removed once `sites` are removed
    path("admin/mfa/qrcode/", QRGeneratorView.as_view(), name="qr"),
    path("admin/", include((maykin_2fa_urlpatterns, "maykin_2fa"))),
    path("admin/", include((webauthn_urlpatterns, "two_factor"))),
    path("admin/", admin.site.urls),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # Simply show the master template.
    path(
        "",
        TemplateView.as_view(
            template_name="index.html",
            extra_context={"version": api_settings.DEFAULT_VERSION},
        ),
        name="home",
    ),
    path("ref/", include("vng_api_common.urls")),
    path("ref/", include("notifications_api_common.urls")),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("api/", include("objects.api.urls")),
]

# NOTE: The staticfiles_urlpatterns also discovers static files (ie. no need to run collectstatic). Both the static
# folder and the media folder are only served via Django if DEBUG = True.
urlpatterns += staticfiles_urlpatterns() + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

if settings.DEBUG and apps.is_installed("debug_toolbar"):
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns


if apps.is_installed("silk"):
    urlpatterns += [path(r"silk/", include("silk.urls", namespace="silk"))]
