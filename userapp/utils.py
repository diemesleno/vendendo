# coding:utf-8
from django.contrib.auth.models import User
from .models import UserComplement
import uuid
import hashlib


def create_user(strategy, details, backend=None, user=None, *args, **kwargs):
    if backend.name == 'google-oauth2':
        if User.objects.filter(email=details['email']).exists():
            user = User.objects.get(email=details['email'])
        else:
            new_account = User()
            new_account.username = hashlib.md5(details['email']).hexdigest()[-30:]
            new_account.email = details['email']
            new_account.first_name = details['first_name']
            new_account.last_name = details['last_name']
            # make password
            salt = uuid.uuid4().hex
            new_pass = str(hashlib.md5(salt.encode() +
                           details['email'].encode()).hexdigest())[-8:]
            new_account.set_password(new_pass)
            new_account.save()

            uc = UserComplement()
            uc.user_account = new_account
            uc.save()

            user = new_account

    return {'strategy': strategy, 'backend': backend, 'details': details, 'user': user, 'args': args, 'kwargs': kwargs}