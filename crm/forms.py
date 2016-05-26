from django import forms
from crm.models import Organization


class OrganizationForm(forms.ModelForm):

    class Meta:
        model = Organization
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.fields["name"].required = True
