from django.test import TestCase
from django.contrib.auth.models import User
from userapp.models import UserComplement
from crm.models import Organization


class UserComplementTests(TestCase):

    
    def create_usercomplement(self, user_test=None, organization_test=None):
        if not user_test:
            user_test = User.objects.create_user(username='user_test',
                                                 email='a@a.com',
                                                 password='1234',
                                                 first_name='name_test')
        if not organization_test:
            organization_test = Organization.objects.create(
                                    name='organization_test')
        return UserComplement.objects.create(
            user_account=user_test,
            organization_active=organization_test)

    def test_usercomplement_creation(self):
        user_complement = self.create_usercomplement()
        self.assertTrue(isinstance(user_complement, UserComplement))

    def test_unicode_label(self):
        user_complement = self.create_usercomplement()
        self.assertEquals('name_test', str(user_complement))
