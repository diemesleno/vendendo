from django.test import TestCase
from crm.models import Organization, UserOrganization, CustomerService
from django.contrib.auth.models import User



class OrganizationTests(TestCase):

    def create_organization(self, name='organization_test'):
        return Organization.objects.create(name=name)

    def setUp(self):
        self.organization = self.create_organization()

    def test_organization_creation(self):
        self.assertTrue(isinstance(self.organization, Organization))

    def test_unicode_label(self):
        self.assertEquals('organization_test', str(self.organization))

    def test_should_have_an_absolute_url_to_index(self):
        url = self.organization.get_absolute_url()
        self.assertEquals('/organizations/', str(url))


class UserOrganizationTests(TestCase):

    def create_user_organization(self, 
                                 organization_name='organization_test',
                                 username= 'user_test',
                                 email='a@ab.com',
                                 first_name='John',
                                 password='A23456@8',
                                 type_user='A',
                                 status_active='A',
                                 code_activating=None):
        user_test = User.objects.create_user(username=username,
                                             email=email,
                                             password=password,
                                             first_name=first_name)
        organization_test = Organization.objects.create(
            name=organization_name)

        return UserOrganization.objects.create(user_account=user_test,
                                               organization=organization_test,
                                               type_user=type_user,
                                               status_active=status_active,
                                               code_activating=code_activating)

    def setUp(self):
        self.user_organization = self.create_user_organization()

    def test_user_organization_creation(self):
        self.assertTrue(isinstance(self.user_organization, UserOrganization))

    def test_unicode_label(self):
        self.assertIn('John (organization_test)', str(self.user_organization))

    def test_should_have_an_absolute_url_to_index(self):
        url = self.user_organization.get_absolute_url()
        self.assertEquals('/sellers/', str(url))


class CustomerServiceTests(TestCase):

    def create_customer_servcie(self, name='service_test', ):
        organization = Organization.objects.create(name='organization_test')
        return CustomerService.objects.create(name=name,organization=organization)

    def setUp(self):
        self.customer_service = self.create_customer_servcie()

    def test_customer_service_creation(self):
        self.assertTrue(isinstance(self.customer_service, CustomerService))

    def test_unicode_label(self):
        self.assertEquals('service_test', str(self.customer_service))

    def test_should_have_an_absolute_url_to_index(self):
        url = self.customer_service.get_absolute_url()
        self.assertEquals('/customerservice/', str(url))
