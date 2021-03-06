import pytest
import json
import time
from tests.test_app import client


def register(client, email, password, password2):
    return client.post('/register', json={'email': email, 'password': password, 'password2': password2})

def login(client, email, password):
    return client.post('/login', json={'email': email, 'password': password})

def logout(client, authorization):
    return client.post('/logout', headers={'Authorization': authorization})

def delete_user(client, authorization):
    return client.delete('/user', headers={'Authorization': authorization})

def delete_url(client, authorization, info: dict):
    return client.delete('/url', json=info, headers={'Authorization': authorization})

def create_url(client, authorization, info: dict):
    return client.post('/url', json=info, headers={'Authorization': authorization})

def get_url(client, authorization, info: dict):
    return client.get('/url', json=info, headers={'Authorization': authorization})

def create_url_public(client, info: dict):
    return client.post('/create', json=info)

def forward_url(client, key):
    return client.get(f'/{key}')

def delete_key(client, authorization, info: dict):
    return client.delete('/key', json=info, headers={'Authorization': authorization})


class TestUrl:

    def test_register_logout(self, client):
        """test register logout"""
        email = "test@gmail.com"
        password = "123456"

        rv = register(client, email, password, password)
        res_data = json.loads(rv.data)
        assert 201 == rv.status_code
        assert 0 == res_data.get('header').get('code')
        assert email == res_data.get('body').get('email')
        assert "" != rv.headers.get('Authorization', "")
        assert None != rv.headers.get('Authorization', None)

        authorization = rv.headers.get('Authorization')
        rv = logout(client, authorization)
        assert 204 == rv.status_code

    def test_login_create_url_delete_url(self, client):
        """test_login_create_url_delete_url"""
        email = "test@gmail.com"
        password = "123456"

        rv = login(client, email, password)
        res_data = json.loads(rv.data)
        assert 200 == rv.status_code
        assert 0 == res_data.get('header').get('code')
        assert email == res_data.get('body').get('email')
        assert "" != rv.headers.get('Authorization', "")
        assert None != rv.headers.get('Authorization', None)

        authorization = rv.headers.get('Authorization')

        key = str(int(time.time()))
        info = {'origin_url': "http://localhost", "key": key}
        rv = create_url(client, authorization, info)
        res_data = json.loads(rv.data)
        assert 201 == rv.status_code
        assert 0 == res_data.get('header').get('code')
        assert key == res_data.get('body').get('key')
        assert None != res_data.get('body').get('domain', None)

        # key existed
        rv = create_url(client, authorization, info)
        res_data = json.loads(rv.data)
        assert 200 == rv.status_code
        assert 10 == res_data.get('header').get('code')

        info = {'key': key}
        rv = delete_url(client, authorization, info)
        res_data = json.loads(rv.data)
        assert 200 == rv.status_code
        assert 0 == res_data.get('header').get('code')

        # delete not exsited
        rv = delete_url(client, authorization, info)
        res_data = json.loads(rv.data)
        assert 200 == rv.status_code
        assert 12 == res_data.get('header').get('code')

    def test_login_delete(self, client):
        """test register delete"""
        email = "test@gmail.com"
        password = "123456"

        rv = login(client, email, password)
        res_data = json.loads(rv.data)
        assert 200 == rv.status_code
        assert 0 == res_data.get('header').get('code')
        assert email == res_data.get('body').get('email')
        assert "" != rv.headers.get('Authorization', "")
        assert None != rv.headers.get('Authorization', None)

        authorization = rv.headers.get('Authorization')
        rv = delete_user(client, authorization)
        assert 204 == rv.status_code

    def test_create_public_url_forward_and_admin_get_delete_url(self, client):
        """test_create_public_url_forward_and_admin_get_delete_url"""

        key = str(int(time.time())+1)
        url = 'http://localhost:8000'
        info = {'origin_url': url, "key": key}
        rv = create_url_public(client, info)
        res_data = json.loads(rv.data)
        assert 201 == rv.status_code
        assert 0 == res_data.get('header').get('code')
        assert key == res_data.get('body').get('key')
        assert None != res_data.get('body').get('domain', None)

        rv = create_url_public(client, info)
        res_data = json.loads(rv.data)
        assert 200 == rv.status_code
        assert 10 == res_data.get('header').get('code')

        rv = forward_url(client, key)
        res_data = rv.data.decode()
        assert 302 == rv.status_code
        assert url in res_data

        rv = forward_url(client, 'errorcase')
        res_data = json.loads(rv.data)
        assert 404 == rv.status_code
        assert 13 == res_data.get('header').get('code')

        """test admin_get_delete_url"""
        email = "xxx@gmail.com"
        password = "password"

        rv = login(client, email, password)
        res_data = json.loads(rv.data)
        assert 200 == rv.status_code
        assert 0 == res_data.get('header').get('code')
        assert email == res_data.get('body').get('email')
        assert "" != rv.headers.get('Authorization', "")
        assert None != rv.headers.get('Authorization', None)

        authorization = rv.headers.get('Authorization')
        get_url_info = {'page': 1, 'count': 10}
        rv = get_url(client, authorization, get_url_info)
        res_data = json.loads(rv.data)
        assert 200 == rv.status_code
        assert 0 == res_data.get('header').get('code')
        assert True == isinstance(res_data.get('body', {}).get('list'), list)

        info = {'key': key}
        rv = delete_url(client, authorization, info)
        res_data = json.loads(rv.data)
        assert 200 == rv.status_code
        assert 0 == res_data.get('header').get('code')

        # delete not exsited
        rv = delete_url(client, authorization, info)
        res_data = json.loads(rv.data)
        assert 200 == rv.status_code
        assert 12 == res_data.get('header').get('code')

        info = {'key': key}
        rv = delete_key(client, authorization, info)
        res_data = json.loads(rv.data)
        assert 200 == rv.status_code
        assert 0 == res_data.get('header').get('code')

        # delete not exsited
        rv = delete_key(client, authorization, info)
        res_data = json.loads(rv.data)
        assert 200 == rv.status_code
        assert 14 == res_data.get('header').get('code')