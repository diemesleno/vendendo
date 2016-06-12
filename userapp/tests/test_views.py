# coding:utf-8
from django.core import mail
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from userapp.views import ListUsers, RegisterUser, EditUser, UserLogin, ResetPassword, EditPassword, Logout
import mock


def add_middleware_to_request(request, middleware_class):
    middleware = middleware_class()
    middleware.process_request(request)
    return request

def add_middleware_to_response(request, middleware_class):
    middleware = middleware_class()
    middleware.process_request(request)
    return request


class LoginTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.data = {"username":"user_test",
                     "email":"a@ab.com",
                     "first_name":"John",
                     "last_name":"Doe",
                     "password":"A23456@8",
                     "organization":"org_teste"}

    def create_user(self, username="user_test", email="a@ab.com", first_name="John", last_name="Doe", password="A23456@8", organization="org_teste"):
        self.data['username'] = username
        self.data['email'] = email
        self.data['first_name'] = first_name
        self.data['last_name'] = last_name
        self.data['password'] = password
        self.data['organization'] = organization

        request = self.factory.post("/newuser/", self.data)
        request.user = AnonymousUser()

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = RegisterUser.as_view()(request)
        return User.objects.get(email=email)

    def test_list_users(self):
        request = self.factory.get("/listusers/")
        request.user = AnonymousUser()

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = ListUsers.as_view()(request)
        self.assertContains(response, "Lista de Usuários")

    def test_register_user_form(self):
        request = self.factory.get("/newuser/")
        request.user = AnonymousUser()

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = RegisterUser.as_view()(request)
        self.assertContains(response, "Cadastro de Usuário")

    def test_register_user_form_valid(self):
        request = self.factory.post("/newuser/", self.data)
        request.user = AnonymousUser()

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = RegisterUser.as_view()(request)
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(email="a@ab.com")
        self.assertEqual(new_user.first_name, "John")

    def test_edit_register_user_form_valid(self):
        request = self.factory.post("/newuser/", self.data)
        request.user = AnonymousUser()
        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()
        response = RegisterUser.as_view()(request)
        new_user = User.objects.get(email="a@ab.com")
        new_data = {"id": new_user.id,
                    "username": "user_test",
                    "email": "a@cd.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "password": "A23456@8",
                    "organization": "org_teste"}
        request = self.factory.post("/newuser/", new_data)
        response = RegisterUser.as_view()(request)
        user_edited = User.objects.get(email="a@cd.com")
        self.assertEqual(new_user.first_name, "John")

    def test_edit_register_user_form_invalid(self):
        request = self.factory.post("/newuser/", self.data)
        request.user = AnonymousUser()
        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()
        response = RegisterUser.as_view()(request)
        new_user = User.objects.get(email="a@ab.com")
        new_data = {"id": new_user.id,
                    "username": "user_test",
                    "email": "a@cd.com"}
        request = self.factory.post("/newuser/", new_data)
        response = RegisterUser.as_view()(request)
        context = response.context_data
        self.assertFalse(context['form'].is_valid())

    def test_edit_user(self):
        request = self.factory.get("/edituser/")
        request.user = self.create_user()

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = EditUser.as_view()(request)
        self.assertContains(response, "Cadastro de Usuário")

    def test_edit_user_form_valid(self):
        new_data = {"email": "a@cd.com",
                    "first_name": "Larry"}
        request = self.factory.post("/edituser/", new_data)
        request.user = self.create_user()
        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()
        response = EditUser.as_view()(request)
        user_edited = User.objects.get(email="a@cd.com")
        self.assertEqual(user_edited.first_name, "Larry")

    def test_a_email_can_not_be_register_twice(self):
        self.create_user(email="a@cd.com", first_name="Walter", last_name="White", organization="Cook")
        new_data = {"email": "a@cd.com",
                    "first_name": "Larry"}
        request = self.factory.post("/edituser/", new_data)
        request.user = self.create_user()
        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()
        response = EditUser.as_view()(request)
        context = response.context_data
        self.assertEqual(context['error'], "Já existe uma conta \
                                             registrada com esse e-mail.")

    def test_logon_of_a_valid_credencial(self):
        self.create_user()
        logon_data = {"email": "a@ab.com", "password": "A23456@8"}
        request = self.factory.post("/", logon_data)
        request.user = AnonymousUser()

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = UserLogin.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_logon_of_a_inactive_credencial(self):
        self.create_user()
        user_created = User.objects.get(email="a@ab.com")
        user_created.is_active = False
        user_created.save()
        logon_data = {"email": "a@ab.com", "password": "A23456@8"}
        request = self.factory.post("/", logon_data)
        request.user = AnonymousUser()

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = UserLogin.as_view()(request)
        context = response.context_data
        self.assertEqual(context['error'], "Este usuário encontra-se, \
                                          inativo. Entre em contato com o \
                                          administrador da conta.")

    def test_logon_of_a_incorrect_credencial(self):
        self.create_user()
        user_created = User.objects.get(email="a@ab.com")
        user_created.save()
        logon_data = {"email": "a@ab.com", "password": "aabbccdd"}
        request = self.factory.post("/", logon_data)
        request.user = AnonymousUser()

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = UserLogin.as_view()(request)
        context = response.context_data
        self.assertEqual(context['error'], "E-mail ou senha incorretos.")

    def test_resetpassword_creates_and_send_a_new_password(self):
        self.create_user()
        data = {"email": "a@ab.com"}
        request = self.factory.post("/resetpwd/", data)
        request.user = AnonymousUser()
        response = ResetPassword.as_view()(request)
        context = response.context_data
        self.assertEqual(context['success'], "Um e-mail foi enviado para você com \
                                            a sua nova senha")

    @mock.patch('userapp.views.send_mail')
    def test_resetpassword_rises_exception(self, mock_mail):
        mock_mail.side_effect = Exception('Fail')

        self.create_user()
        data = {"email": "a@ab.com"}
        request = self.factory.post("/resetpwd/", data)
        request.user = AnonymousUser() 

        response = ResetPassword.as_view()(request)
        context = response.context_data
        self.assertEqual(context['error'], "Erro interno: Fail")

    def test_can_not_reset_password_for_inactive_user(self):
        self.create_user()
        user_created = User.objects.get(email="a@ab.com")
        user_created.is_active = False
        user_created.save()
        reset_data = {"email": "a@ab.com"}
        request = self.factory.post("/", reset_data)
        request.user = AnonymousUser()

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = ResetPassword.as_view()(request)
        context = response.context_data
        self.assertEqual(context['error'], "Este usuário encontra-se, \
                                         inativo. Entre em contato com o \
                                         administrador da conta.")
    
    def test_view_edit_password(self):
        self.create_user()
        request = self.factory.get("/editpwd/")
        request.user = User.objects.get(email="a@ab.com")

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = EditPassword.as_view()(request)
        self.assertContains(response, "Alterar Senha")

    def test_edit_password_should_return_success_context(self):
        self.create_user()
        form_data = {"password":"A23456@9"}
        request = self.factory.post("/editpwd/", form_data)
        request.user = User.objects.get(email="a@ab.com")

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = EditPassword.as_view()(request)
        context = response.context_data
        self.assertTrue(context['success'])
        self.assertEqual(context['success'], "Sua senha foi alterada com \
                                     sucesso")

    def test_view_logout_should_redirect(self):
        request = self.factory.get("/logout/")
        request.user = AnonymousUser()

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = Logout.as_view()(request)
        self.assertEqual(response.status_code, 302)
