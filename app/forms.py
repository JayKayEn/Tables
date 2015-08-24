from django import forms
from django.forms import HiddenInput
from .models import Table

class NewTableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ('name',)

class EditTableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = '__all__'
        exclude = ['user', 'name', 'people', 'needs_review']

