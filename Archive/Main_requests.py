import requests
import urllib3
import base64
import json
from pprint import pprint

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = 'https://192.168.33.50'
username = input('Enter the username: ')
password = input('Enter the password: ')

def decode_password():
    """ Generate Base64 encoding using the base64 library """
    return base64.b64encode('{}:{}'.format(username, password).encode('UTF-8')).decode('ASCII')

def generate_session_token(encoded):
    """ Generate the session token for FMC """
    url = base_url + "/api/fmc_platform/v1/auth/generatetoken"
    headers = {
    'Content-Type': "application/json",
    'Authorization': "Basic {}".format(encoded),
    }
    response = requests.post(url, headers=headers, verify=False)
    token = response.headers['X-auth-access-token']
    uuid = response.headers['DOMAIN_UUID']
    return token, uuid

def get_access_policies(token, uuid):
    url = '{}/api/fmc_config/v1/domain/{}/policy/accesspolicies'.format(base_url, uuid)
    headers = {
    'Content-Type': "application/json",
    'X-auth-access-token': token,
    }
    response = requests.get(url, headers=headers, verify=False)
    acp_name = response.json()['items'][0]['name']
    acp_id = response.json()['items'][0]['id']
    return acp_id

def get_access_rules(acp_id):
    url = '{}/api/fmc_config/v1/domain/{}/policy/accesspolicies/{}/accessrules'.format(base_url, uuid, acp_id)
    headers = {
    'Content-Type': "application/json",
    'X-auth-access-token': token,
    }
    response = requests.get(url=url, headers=headers, verify=False)
    id_list = [item['id'] for item in response.json()['items']]
    name_list = [item['name'] for item in response.json()['items']]
    print(id_list)
    for rule_id in id_list:
        print("**********")
        get_access_rule(rule_id)
        print("**********")

def get_access_rule(rule_id):
    url = '{}/api/fmc_config/v1/domain/{}/policy/accesspolicies/{}/accessrules/{}'.format(base_url, uuid, acp_id, rule_id)
    headers = {
    'Content-Type': "application/json",
    'X-auth-access-token': token,
    }
    response = requests.get(url=url, headers=headers, verify=False)
    pprint(response.json())

encoded = decode_password()
token, uuid = generate_session_token(encoded)
acp_id = get_access_policies(token, uuid)
get_access_rules(acp_id)