from dal import autocomplete
from django import forms
<<<<<<< HEAD
from shopping_tool.models import WpUser
=======
from shopping_tool.models import WpUsers
>>>>>>> 09909669f33c3392509e59c85d3972a6afeeaeeb

# for autocomplete user search
class PersonForm(forms.ModelForm):
    class Meta:
<<<<<<< HEAD
        model = WpUser
=======
        model = WpUsers
>>>>>>> 09909669f33c3392509e59c85d3972a6afeeaeeb
        fields = ('__all__')
        widgets = {
            'stylist': autocomplete.ModelSelect2(url='user-autocomplete'),
            'director': autocomplete.ModelSelect2(url='user-autocomplete'),
            'manager': autocomplete.ModelSelect2(url='user-autocomplete'),
            'asm': autocomplete.ModelSelect2(url='user-autocomplete'),
        }