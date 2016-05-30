# coding:utf-8
from django import forms
from crm.models import Organization, UserOrganization
from userapp.models import UserComplement
from django.contrib.auth.models import User


class OrganizationForm(forms.ModelForm):

    class Meta:
        model = Organization
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['name'].label = 'Nome'
        self.fields['name'].widget.attrs.update({'class': 'form-control'})


class SellerFindForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(SellerFindForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['email'].label = 'E-mail do Vendedor'
        self.fields['email'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super(SellerFindForm, self).clean()
        email = cleaned_data.get('email')
        # Obtain user admin and organization logon
        user_account = User.objects.get(id=self.user.id)
        organization = UserComplement.objects.get(
                           user_account=user_account).organization_active
        # Verify if new e-mail
        if User.objects.filter(email=email).exists():
            seller = User.objects.get(email=email)
            if UserOrganization.objects.filter(
                user_account=seller,
                organization=organization).exists():
                self.add_error('email', 'O vendedor já faz parte desta organização')
        return cleaned_data


class SellerForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name',
                  'last_name',)

    def __init__(self, *args, **kwargs):
        super(SellerForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['first_name'].label = 'Nome'
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})

        self.fields['last_name'].required = False
        self.fields['last_name'].label = 'Sobrenome'
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
