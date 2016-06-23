# coding:utf-8
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from crm.models import Organization, UserOrganization
from crm.views import *
import mock


def add_middleware_to_request(request, middleware_class):
    middleware = middleware_class()
    middleware.process_request(request)
    return request

def create_user_organization(user_test=None, organization_test=None):
    if not user_test:
        user_test = User.objects.create_user(username='user_test',
                                             email='a@a.com',
                                             password='1234',
                                             first_name='name_test')
    if not organization_test:
        organization_test = Organization.objects.create(
                                name='organization_test')

    UserComplement.objects.create(user_account=user_test,
                                  organization_active=organization_test)
    return UserOrganization.objects.create(
        user_account=user_test,
        organization=organization_test,
        type_user='A',
        status_active='A')

class OrganizationTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        user_organization = create_user_organization()
        self.user_session = user_organization.user_account

    def test_organization_index_should_listing_organizations_of_the_user(self):
        request = self.factory.get("/organizations/")
        request.user = self.user_session

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = OrganizationIndex.as_view()(request)
        self.assertContains(response, "Minhas Organizações")
        self.assertContains(response, "organization_test")


class SendxTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.user = AnonymousUser()

    @mock.patch('crm.views.send_mail')
    def test_send_invite_returns_exception_message(self, mock_mail):
        mock_mail.side_effect = Exception('Fail')
        user_organization = create_user_organization()
        self.request.user = user_organization.user_account
        result = Sendx.send_invite(self, user_organization)
        self.assertEqual(result, "Erro interno: Fail") 

    @mock.patch('crm.views.send_mail')
    def test_send_invite_should_returns_true(self, mock_mail):
        user_organization = create_user_organization()
        self.request.user = user_organization.user_account
        result = Sendx.send_invite(self, user_organization)
        self.assertTrue(result) 

