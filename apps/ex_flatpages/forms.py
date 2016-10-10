from django.contrib.flatpages.models import FlatPage
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class FlatPageForm(forms.ModelForm):
    class Meta:
        model = FlatPage
        fields = '__all__'
        widgets = {
            'content': CKEditorUploadingWidget()
        }
