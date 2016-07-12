# coding:utf-8
from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from crm.models import Organization, UserOrganization
from django.conf import settings
from importlib import import_module
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

def setup_view(view, request, *args, **kwargs):
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


class OrganizationTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        user_organization = create_user_organization()
        self.user_session = user_organization.user_account
        self.data = {"name":"organization_test_2"}

    def test_organization_index_should_listing_organizations_of_the_user(self):
        request = self.factory.get("/organizations/")
        request.user = self.user_session

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = OrganizationIndex.as_view()(request)
        self.assertContains(response, "Minhas Organizações")
        self.assertContains(response, "organization_test")

    def test_create_a_new_organization_form_valid(self):
        request = self.factory.post("/organization/add/", self.data)
        request.user = self.user_session

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = OrganizationCreate.as_view()(request)
        self.assertEqual(response.status_code, 302)
        user_organization = UserOrganization.objects.filter(
                                user_account=request.user)
        self.assertIn('organization_test_2',
                      [uorg.organization.name for uorg in user_organization])

    def test_user_that_create_the_organization_should_be_the_admin_of_it(self):
        request = self.factory.post("/organization/add/", self.data)
        request.user = self.user_session

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = OrganizationCreate.as_view()(request)
        user_organization = UserOrganization.objects.filter(
                                user_account=request.user,
                                type_user='A')
        self.assertIn('organization_test_2',
                      [uorg.organization.name for uorg in user_organization])

    def test_the_new_organization_should_be_initial_status_active(self):
        request = self.factory.post("/organization/add/", self.data)
        request.user = self.user_session

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = OrganizationCreate.as_view()(request)
        user_organization = UserOrganization.objects.filter(
                                user_account=request.user,
                                status_active='A')
        self.assertIn('organization_test_2',
                      [uorg.organization.name for uorg in user_organization])

    def test_only_the_admin_of_organization_can_update_it(self):
        # create a new user
        user2 = User.objects.create_user(username='user_test_2',
                                         email='b@b.com',
                                         password='4321',
                                         first_name='name_test_2')
        org2 = Organization.objects.create(name='organization_test_2')
        user_organization_2 = create_user_organization(
                                  user_test=user2,
                                  organization_test=org2)
        #run the test
        request = self.factory.get(reverse('crm:organization-update',kwargs={'pk': 1}))
        request.user = self.user_session

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = setup_view(OrganizationUpdate(), request)
        response.kwargs = {'pk': user_organization_2.organization.id}
        response = response.dispatch(request)
        self.assertEqual(response.status_code, 302)


class SellerTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        user_organization = create_user_organization()
        self.user_session = user_organization.user_account
        self.data = {"first_name":"John",
                     "last_name":"Doe"}

    def test_create_a_new_seller_form_valid(self):
        request = self.factory.post("/seller/add/", self.data)
        request.user = self.user_session
        request = add_middleware_to_request(request, SessionMiddleware)
        request.session["email_find"] = "johndoe@a.com"
        request.session.save()
        response = SellerCreate.as_view()(request)
        self.assertEqual(response.status_code, 302)

    @mock.patch('crm.views.Sendx.send_invite')
    def test_create_a_new_seller_raises_exception(self, mock_mail):
        mock_mail.side_effect = Exception('Fail')
        request = self.factory.post("/seller/add/", self.data)
        request.user = self.user_session
        request = add_middleware_to_request(request, SessionMiddleware)
        request.session["email_find"] = "johndoe@a.com"
        request.session.save()
        with self.assertRaises(Exception):
            response = SellerCreate.as_view()(request)

    def test_join_a_new_seller_form_valid(self):
        request = self.factory.post("/seller/add/", self.data)
        request.user = self.user_session
        request = add_middleware_to_request(request, SessionMiddleware)
        request.session["email_find"] = "johndoe@a.com"
        request.session.save()
        response = SellerCreate.as_view()(request)

        request = self.factory.post("/seller/join/", self.data)
        request.user = self.user_session
        request = add_middleware_to_request(request, SessionMiddleware)
        request.session["email_find"] = "johndoe@a.com"
        request.session.save()
        response = SellerJoin.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_seller_deactivate_should_update_status(self):
        request = self.factory.post("/seller/add/", self.data)
        request.user = self.user_session
        request = add_middleware_to_request(request, SessionMiddleware)
        request.session["email_find"] = "johndoe@a.com"
        request.session.save()
        response = SellerCreate.as_view()(request)
        #run the test
        request = self.factory.post(reverse('crm:seller-deactivate',kwargs={'pk': 1}))
        request.user = self.user_session

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        user_account = User.objects.get(email="johndoe@a.com")
        seller = UserOrganization.objects.get(user_account=user_account)
        response = setup_view(SellerDeactivate(), request)
        response.kwargs = {'pk': seller.id}
        response = response.post(request)
        seller_deactivate = UserOrganization.objects.get(user_account=user_account)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(seller_deactivate.status_active, "I")

    def test_invite_active_only_valid_code(self):
        request = self.factory.post("/seller/add/", self.data)
        request.user = self.user_session
        request = add_middleware_to_request(request, SessionMiddleware)
        request.session["email_find"] = "johndoe@a.com"
        request.session.save()
        response = SellerCreate.as_view()(request)

        user_account = User.objects.get(email="johndoe@a.com")
        user_organization = UserOrganization.objects.get(user_account=user_account)
        code_activate = user_organization.code_activating

        request = self.factory.get('invite/activate',{'code': code_activate})
        request.user = self.user_session
        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()
        response = SellerInviteActivate.as_view()(request)

        user_account = User.objects.get(email="johndoe@a.com")
        user_organization = UserOrganization.objects.get(user_account=user_account)

        self.assertEqual(user_organization.status_active, "A")

    @mock.patch('crm.views.Sendx.send_invite')
    def test_seller_send_invite(self, mock_mail):
        mock_mail.side_effect = "OK"
        request = self.factory.post("/seller/add/", self.data)
        request.user = self.user_session
        request = add_middleware_to_request(request, SessionMiddleware)
        request.session["email_find"] = "johndoe@a.com"
        request.session.save()
        response = SellerCreate.as_view()(request)
        # run test
        request = self.factory.post(reverse('crm:seller-invite',kwargs={'pk': 1}))
        request.user = self.user_session

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        user_account = User.objects.get(email="johndoe@a.com")
        seller = UserOrganization.objects.get(user_account=user_account)
        response = setup_view(SellerInvite(), request)
        response.kwargs = {'pk': seller.id}
        response = response.post(request)
        self.assertEqual(response.status_code, 302)


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

