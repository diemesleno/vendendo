# coding:utf-8
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from userapp.views import ListUsers, RegisterUser


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

    def test_valid_register_user_form(self):
        data = {"username":"user_test",
                "email":"a@ab.com",
                "first_name":"John",
                "last_name":"Doe",
                "password":"A23456@8",
                "organization":"org_teste"}
        request = self.factory.post("/newuser/", data)
        request.user = AnonymousUser()

        request = add_middleware_to_request(request, SessionMiddleware)
        request.session.save()

        response = RegisterUser.as_view()(request)
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(email="a@ab.com")
        self.assertEqual(new_user.first_name, "John")
