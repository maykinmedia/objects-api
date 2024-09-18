from django.contrib.sites.requests import RequestSite

from maykin_2fa.views import QRGeneratorView as _QRGeneratorView


class QRGeneratorView(_QRGeneratorView):
    def get_issuer(self):
        return RequestSite(self.request).name
