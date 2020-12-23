from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from vng_api_common.utils import get_uuid_from_path
from zds_client.client import ClientError
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from .models import ObjectType


def get_object_type_choices():
    # just iterate throught all orc services
    # TODO filter on objecttype services
    choices = []
    for service in Service.objects.filter(api_type=APITypes.orc).order_by("label"):
        client = service.build_client()
        try:
            response = client.list("objecttype")
        except ClientError:
            continue
        else:
            group_choices = [
                (object_type["url"], f"{object_type['name']}")
                for object_type in response
            ]
            choices.append((service.label, group_choices))

    return choices


class ObjectTypeForm(forms.ModelForm):
    object_type = forms.ChoiceField(
        choices=get_object_type_choices, widget=forms.RadioSelect
    )

    class Meta:
        model = ObjectType
        fields = ("object_type",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get("instance")
        if instance:
            self.fields["object_type"].initial = instance.url

    def save(self, *args, **kwargs):
        url = self.cleaned_data["object_type"]
        self.instance.service = Service.get_service(url)
        self.instance.uuid = get_uuid_from_path(url)

        return super().save(*args, **kwargs)

    def clean_object_type(self):
        object_type_url = self.cleaned_data["object_type"]
        try:
            ObjectType.objects.get_by_url(object_type_url)
        except ObjectType.DoesNotExist:
            return object_type_url

        raise ValidationError(_("This object type already exists"))
