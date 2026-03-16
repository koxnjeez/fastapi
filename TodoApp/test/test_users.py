from .utils import *
from ..routers.users import get_current_user, get_db
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_user(test_user):
  response = client.get('/users/profile')
  assert response.status_code == status.HTTP_200_OK
  assert response.json()['username'] == 'koxnjeez'
  assert response.json()['email'] == 'v.cherv@gmail.com'
  assert response.json()['first_name'] == 'Vlad'
  assert response.json()['last_name'] == 'Chervonenko'
  assert response.json()['role'] == 'admin'
  assert response.json()['phone_number'] == '111010101002'

def test_change_password(test_user):
  response = client.put('/users/profile/change_pass/', json={
    'actual_password': '123123',
    'new_password': '666666'
  })
  assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_invalid_current_password(test_user):
  response = client.put('/users/profile/change_pass/', json={
    'actual_password': '999999999',
    'new_password': '666666'
  })
  assert response.status_code == status.HTTP_401_UNAUTHORIZED
  assert response.json() == {'detail': 'Password change error.'}

def test_phone_number_change(test_user):
  response = client.put('/users/profile/12398127398')
  assert response.status_code == status.HTTP_204_NO_CONTENT