# coding:utf-8
from django import forms
from crm.models import Organization, UserOrganization, OccupationArea,\
                       Customer, SaleStage, CustomerService, Opportunity,\
                       Activity
from userapp.models import UserComplement
from django.contrib.auth.models import User
from django.forms.widgets import RadioSelect
from django.contrib.admin.widgets import AdminDateWidget


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
                    user_account=seller, organization=organization).exists():
                    self.add_error('email', 'O vendedor já faz parte desta \
                                    organização')
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


class OccupationAreaForm(forms.ModelForm):

    class Meta:
        model = OccupationArea
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(OccupationAreaForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['name'].label = 'Nome'
        self.fields['name'].widget.attrs.update({'class': 'form-control'})


class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = ('name',
                  'legal_personality',
                  'category',
                  'occupationarea',
                  'relevance',
                  'notes',
                  'contact1_name',
                  'contact1_tel',
                  'contact1_email',
                  'contact1_position',
                  'contact2_name',
                  'contact2_tel',
                  'contact2_email',
                  'contact2_position',
                  'contact3_name',
                  'contact3_tel',
                  'contact3_email',
                  'contact3_position',)

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['name'].label = 'Nome'
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['legal_personality'].required = True
        self.fields['legal_personality'].label = 'Tipo de Pessoa'
        self.fields['legal_personality'].widget = forms.RadioSelect(choices=Customer.legal_personality_choices)
        self.fields['category'].required = True
        self.fields['category'].label = 'Categoria'
        self.fields['category'].widget = forms.RadioSelect(choices=Customer.category_choices)
        self.fields['occupationarea'].required = True
        self.fields['occupationarea'].label = 'Área de Atuação'
        self.fields['occupationarea'].widget.attrs.update({'class': 'form-control'})
        self.fields['relevance'].required = True
        self.fields['relevance'].label = 'Relevância'
        self.fields['relevance'].widget.attrs.update({'class': 'form-control'})
        self.fields['notes'].required = False
        self.fields['notes'].label = 'Notas'
        self.fields['notes'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact1_name'].required = True
        self.fields['contact1_name'].label = 'Nome'
        self.fields['contact1_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact1_tel'].required = True
        self.fields['contact1_tel'].label = 'Telefone'
        self.fields['contact1_tel'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact1_email'].required = True
        self.fields['contact1_email'].label = 'E-mail'
        self.fields['contact1_email'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact1_position'].required = True
        self.fields['contact1_position'].label = 'Cargo'
        self.fields['contact1_position'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact2_name'].required = False
        self.fields['contact2_name'].label = 'Nome'
        self.fields['contact2_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact2_tel'].required = False
        self.fields['contact2_tel'].label = 'Telefone'
        self.fields['contact2_tel'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact2_email'].required = False
        self.fields['contact2_email'].label = 'E-mail'
        self.fields['contact2_email'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact2_position'].required = False
        self.fields['contact2_position'].label = 'Cargo'
        self.fields['contact2_position'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact3_name'].required = False
        self.fields['contact3_name'].label = 'Nome'
        self.fields['contact3_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact3_tel'].required = False
        self.fields['contact3_tel'].label = 'Telefone'
        self.fields['contact3_tel'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact3_email'].required = False
        self.fields['contact3_email'].label = 'E-mail'
        self.fields['contact3_email'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact3_position'].required = False
        self.fields['contact3_position'].label = 'Cargo'
        self.fields['contact3_position'].widget.attrs.update({'class': 'form-control'})


class SaleStageForm(forms.ModelForm):

    class Meta:
        model = SaleStage
        fields = ('name','final_stage','add_customer')

    def __init__(self, *args, **kwargs):
        super(SaleStageForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['name'].label = 'Nome'
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        # field final_stage
        self.fields['final_stage'].required = False
        self.fields['final_stage'].label = 'Fase final'
        self.fields['final_stage'].widget = forms.CheckboxInput()
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
        fields = ('customer', 'stage', 'expected_month')

    def __init__(self, organization, *args, **kwargs):
        super(OpportunityForm, self).__init__(*args, **kwargs)
        # field customer
        self.fields['customer'].required = True
        self.fields['customer'].label = 'Cliente'
        self.fields['customer'].widget.attrs.update({'class': 'form-control'})
        self.fields['customer'].queryset = Customer.objects.filter(organization=organization)
        # field stage
        self.fields['stage'].required = True
        self.fields['stage'].label = 'Etapa'
        self.fields['stage'].widget.attrs.update({'class': 'form-control'})
        # field expected_month
        self.fields['expected_month'].required = False
        self.fields['expected_month'].label = 'Mês estimado'
        self.fields['expected_month'].widget.attrs.update({'class': 'form-control'})


class ActivityForm(forms.ModelForm):

    class Meta:
        model = Activity
        fields = ('title', 'description', 'opportunity', 'type_activity', 'details', 'deadline', 'completed',)

    def __init__(self, organization, *args, **kwargs):
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
        self.fields['opportunity'].queryset = Opportunity.objects.filter(organization=organization, stage__final_stage=False)
        # field type_activity
        self.fields['type_activity'].required = False
        self.fields['type_activity'].label = 'Tipo de Atividade'
        self.fields['type_activity'].widget.attrs.update({'class': 'form-control'})
        # field details
        self.fields['details'].required = False
        self.fields['details'].label = 'Detalhes'
        self.fields['details'].widget.attrs.update({'class': 'form-control'})
        # field deadline
        self.fields['deadline'].required = False
        self.fields['deadline'].label = 'Prazo'
        self.fields['deadline'].widget = forms.widgets.DateInput(format="%d/%m/%Y %H:%M")
        self.fields['deadline'].input_formats = ['%d/%m/%Y %H:%M']
        self.fields['deadline'].widget.attrs.update({'class': 'form-control'})
        # field completed
        self.fields['completed'].required = False
        self.fields['completed'].label = 'Concluída'
        self.fields['completed'].widget = forms.CheckboxInput()
