from dal import autocomplete
from django import forms
from shopping_tool.models import WpUsers

# for autocomplete user search
class PersonForm(forms.ModelForm):
    class Meta:
        model = WpUsers
        fields = ('__all__')
        widgets = {
            'stylist': autocomplete.ModelSelect2(url='user-autocomplete', forward=('stylist',)),
            'director': autocomplete.ModelSelect2(url='user-autocomplete', forward=('director',)),
            'manager': autocomplete.ModelSelect2(url='user-autocomplete', forward=('manager',)),
            'asm': autocomplete.ModelSelect2(url='user-autocomplete', forward=('asm',)),

        }