from dal import autocomplete
from django import forms
from shopping_tool.models import WpUser

# for autocomplete user search
class PersonForm(forms.ModelForm):
    class Meta:
        model = WpUser
        fields = ('__all__')
        widgets = {
            'stylist': autocomplete.ModelSelect2(url='user-autocomplete'),
            'director': autocomplete.ModelSelect2(url='user-autocomplete'),
            'manager': autocomplete.ModelSelect2(url='user-autocomplete'),
            'asm': autocomplete.ModelSelect2(url='user-autocomplete'),
        }