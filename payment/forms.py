from django.forms import ModelForm

from .models import ShippingAddress


class ShippingForm(ModelForm):

    class Meta:

        model = ShippingAddress

        exclude = ['user']