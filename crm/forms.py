# coding:utf-8
from django import forms
from crm.models import Organization, UserOrganization, OccupationArea,\
                       Customer, SaleStage, CustomerService, Opportunity,\
                       Activity
from userapp.models import UserComplement
from django.contrib.auth.models import User
from django.forms.widgets import RadioSelect
from django.contrib.admin.widgets import AdminDateWidget
from django.core.validators import RegexValidator


class OrganizationForm(forms.ModelForm):

    class Meta:
        model = Organization
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['name'].label = 'Nome'
        self.fields['name'].widget.attrs.update({'class': 'form-control'})


class MemberFindForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(MemberFindForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['email'].label = 'E-mail'
        self.fields['email'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super(MemberFindForm, self).clean()
        email = cleaned_data.get('email')
        # Obtain user admin and organization logon
        user_account = User.objects.get(id=self.user.id)
        organization = UserComplement.objects.get(
                           user_account=user_account).organization_active
        # Verify if new e-mail
        if User.objects.filter(email=email).exists():
            member = User.objects.get(email=email)
            if UserOrganization.objects.filter(
                    user_account=member, organization=organization).exists():
                    self.add_error('email', 'Esse usuário já é membro desta \
                                    organização')
        return cleaned_data


class MemberForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name',
                  'last_name',)

    def __init__(self, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['first_name'].label = 'Nome'
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})

        self.fields['last_name'].required = False
        self.fields['last_name'].label = 'Sobrenome'
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})


class OccupationAreaForm(forms.ModelForm):

    class Meta:
        model = OccupationArea
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(OccupationAreaForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['name'].label = 'Nome'
        self.fields['name'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super(OccupationAreaForm, self).clean()
        name = cleaned_data.get('name')
        # Obtain user admin and organization logon
        user_account = User.objects.get(id=self.user.id)
        organization = UserComplement.objects.get(
                           user_account=user_account).organization_active
        # Verify if a new occupation area 
        if OccupationArea.objects.filter(organization=organization,name=name).exists():
            self.add_error('name', 'Já existe um segmento com este nome')
        return cleaned_data


class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = ('name',
                  'category',
                  'occupationarea',
                  'notes',
                  'responsible_seller',)

    def __init__(self, organization, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['name'].label = 'Nome'
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].required = True
        self.fields['category'].label = 'Categoria'
        self.fields['category'].widget = forms.RadioSelect(choices=Customer.category_choices)
        self.fields['occupationarea'].required = True
        self.fields['occupationarea'].label = 'Segmento'
        self.fields['occupationarea'].widget.attrs.update({'class': 'form-control'})
        self.fields['occupationarea'].queryset = OccupationArea.objects.filter(organization=organization)
        self.fields['notes'].required = False
        self.fields['notes'].label = 'Notas'
        self.fields['notes'].widget.attrs.update({'class': 'form-control'})
        # field seller
        self.fields['responsible_seller'].required = False
        self.fields['responsible_seller'].label = 'Gerente da conta'
        self.fields['responsible_seller'].widget.attrs.update({'class': 'form-control'})
        self.fields['responsible_seller'].choices = [(user.pk, user.get_full_name()) for user in User.objects.filter(userorganization__organization=organization)]


class SaleStageForm(forms.ModelForm):

    class Meta:
        model = SaleStage
        fields = ('name','final_stage','conclusion','add_customer')

    def __init__(self, *args, **kwargs):
        super(SaleStageForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['name'].label = 'Nome'
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        # field final_stage
        self.fields['final_stage'].required = False
        self.fields['final_stage'].label = 'Fase final'
        self.fields['final_stage'].widget = forms.CheckboxInput()
        # field conclusion
        self.fields['conclusion'].required = False
        self.fields['conclusion'].label = 'Conclusão da fase'
        self.fields['conclusion'].widget.attrs.update({'class': 'form-control'})
        # field add_customer
        self.fields['add_customer'].required = False
        self.fields['add_customer'].label = 'Adicionar cliente na base'
        self.fields['add_customer'].widget = forms.CheckboxInput()


class CustomerServiceForm(forms.ModelForm):

    class Meta:
        model = CustomerService
        fields = ('name', 'definition', 'description', 'notes', 'status',)

    def __init__(self, *args, **kwargs):
        super(CustomerServiceForm, self).__init__(*args, **kwargs)
        # field name
        self.fields['name'].required = True
        self.fields['name'].label = 'Nome'
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        # field definition
        self.fields['definition'].required = True
        self.fields['definition'].label = 'Tipo'
        self.fields['definition'].widget.attrs.update({'class': 'form-control'})
        # field description
        self.fields['description'].required = False
        self.fields['description'].label = 'Descrição'
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        # field notes
        self.fields['notes'].required = False
        self.fields['notes'].label = 'Notas'
        self.fields['notes'].widget.attrs.update({'class': 'form-control'})
        # field status
        self.fields['status'].required = True
        self.fields['status'].label = 'Status'
        self.fields['status'].widget.attrs.update({'class': 'form-control'})


class OpportunityForm(forms.ModelForm):

    class Meta:
        model = Opportunity
        fields = ('customer', 'description_opportunity', 'stage', 'seller', 'expected_month')

    def __init__(self, organization, *args, **kwargs):
        super(OpportunityForm, self).__init__(*args, **kwargs)
        # field customer
        self.fields['customer'].required = True
        self.fields['customer'].label = 'Cliente'
        self.fields['customer'].widget.attrs.update({'class': 'form-control'})
        self.fields['customer'].queryset = Customer.objects.filter(organization=organization)
        # field description_opportunity
        self.fields['description_opportunity'].required = True
        self.fields['description_opportunity'].label = 'Descrição'
        self.fields['description_opportunity'].widget.attrs.update({'class': 'form-control'})
        # field stage
        self.fields['stage'].required = True
        self.fields['stage'].label = 'Etapa'
        self.fields['stage'].widget.attrs.update({'class': 'form-control'})
        self.fields['stage'].queryset = SaleStage.objects.filter(organization=organization)
        # field seller
        self.fields['seller'].required = False
        self.fields['seller'].label = 'Vendedor'
        self.fields['seller'].widget.attrs.update({'class': 'form-control'})
        self.fields['seller'].choices = [(user.pk, user.get_full_name()) for user in User.objects.filter(userorganization__organization=organization)]
        # field expected_month
        self.fields['expected_month'].required = False
        self.fields['expected_month'].label = 'Mês estimado'
        my_validator = RegexValidator(r"\d{2}/\d{4}", "Use o formato mm/aaaa")
        self.fields['expected_month'].validators = [my_validator]
        self.fields['expected_month'].widget.attrs.update({'class': 'form-control'})
        self.fields['expected_month'].help_text="Por favor, use o formato: MM/AAAA."


class ActivityForm(forms.ModelForm):

    class Meta:
        model = Activity
        fields = ('title', 'description', 'opportunity', 'type_activity', 'details', 'deadline', 'completed',)

    def __init__(self, organization, user, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)
        # field title
        self.fields['title'].required = True
        self.fields['title'].label = 'Título'
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        # field description
        self.fields['description'].required = True
        self.fields['description'].label = 'Descrição'
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        # field opportunity
        self.fields['opportunity'].required = True
        self.fields['opportunity'].label = 'Oportunidade'
        self.fields['opportunity'].widget.attrs.update({'class': 'form-control'})
        type_user = UserOrganization.objects.get(user_account=user, organization=organization).type_user
        if type_user == "A" or type_user == "M":
            self.fields['opportunity'].queryset = Opportunity.objects.filter(organization=organization, stage__final_stage=False).order_by('customer')
        elif type_user == "S":
            self.fields['opportunity'].queryset = Opportunity.objects.filter(organization=organization, stage__final_stage=False, seller=user).order_by('customer')
        # field type_activity
        self.fields['type_activity'].required = False
        self.fields['type_activity'].label = 'Tipo de Atividade'
        self.fields['type_activity'].widget.attrs.update({'class': 'form-control'})
        # field details
        self.fields['details'].required = False
        self.fields['details'].label = 'Detalhes'
        self.fields['details'].widget.attrs.update({'class': 'form-control'})
        # field deadline
        self.fields['deadline'].required = True
        self.fields['deadline'].label = 'Prazo'
        self.fields['deadline'].widget = forms.widgets.DateInput(format="%d/%m/%Y %H:%M")
        self.fields['deadline'].input_formats = ['%d/%m/%Y %H:%M']
        self.fields['deadline'].widget.attrs.update({'class': 'form-control'})
        self.fields['deadline'].help_text="Por favor, use o formato: DD/MM/AAAA HH:MM."
        # field completed
        self.fields['completed'].required = False
        self.fields['completed'].label = 'Concluída'
        self.fields['completed'].widget = forms.CheckboxInput()
