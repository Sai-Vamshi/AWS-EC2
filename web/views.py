import uuid

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from yellowant import YellowAnt
from django.urls import reverse
from yellowant_api.models import YellowAntRedirectState, UserIntegration, awsec2
#from .forms import UserForm
from django.contrib.auth import authenticate, login
import boto3
import datetime , json
import requests
# Create your views here.


"""def home(request, path):
    return HttpResponseRedirect(reverse('accounts'))

def home2(request):
    return HttpResponseRedirect(reverse('accounts'))


def get_accounts(request):
    # print 'entered'
    if request.user.is_authenticated:
        user = request.user
        accounts = []
        fd_accounts = UserIntegration.objects.filter(yellowant_user_id=user.id)
        # print fd_accounts
        for account in fd_accounts:
            # a = accountSettings.objects.get(user=account).new_ticket_notification
            # if a == 0:

            accounts.append({'integration_id': account.yellowant_integration_id,
                             'invoke_name': account.yellowant_integration_user_invoke_name,
                             'integrated': True if account.api_token != None else False})
            # print accountSettings.objects.get(user=account).new_ticket_notification

        return HttpResponse(json.dumps(accounts), content_type="application/json")
    else:
        return HttpResponse([])


def listAccounts(request):
    # print request.user.id
    if request.user.is_authenticated:
        return render(request, 'list_accounts.html', {
                      'login_status': 'Logged in',
                      'base_url':"/market/applications/{}/accounts/".format(settings.YA_APP_ID),
                      'createyaaccountredirect': "/market/applications/{}/createyaaccountredirect/".format(settings.YA_APP_ID)})
    else:
        redirect_url = '/login/'
        return render(request, 'yellowant_generic.html',
                      {
                          'message_code': 401,
                          'message_text': "Please Login to continue",
                          'return_url': redirect_url,
                          'return_url_text': "Login",
                          'message_type': 0
                      },
                      status=200, )


def apikey(request):
    if request.method == "POST":
        data=json.loads(request.body)

        try:
            aby = UserIntegration.objects.get(yellowant_integration_id = data['yellowant_integration_id'], yellowant_user_id=request.user.id)
        except UserIntegration.DoesNotExist:
            return ("Invalid credentials")

        api_token = data['api_token']
        api_secret = data['api_secret']
        api_region = data['api_region']

        try:
            client = boto3.client(service_name='cloudwatch', region_name=api_region, api_version=None, use_ssl=True,
                                  verify=None, endpoint_url=None, aws_access_key_id=api_token,
                                  aws_secret_access_key=api_secret, aws_session_token=None,
                                  config=None)
        except:
            return HttpResponse("Invalid credentials. Please try again")

        yellowant_integration_id = data['yellowant_integration_id']
        inst = UserIntegration.objects.get(yellowant_integration_id=yellowant_integration_id)
        inst.api_token = api_token
        inst.api_secret = api_secret
        inst.api_region = api_region
        inst.save()
    return HttpResponse("Registered")


def accountDetails(request):
    if request.method == 'POST':
        # print request.body
        data = json.loads(request.body)
        integration_id = data['integration_id']
        try:
            cw = UserIntegration.objects.get(yellowant_integration_id=integration_id, yellowant_user_id=request.user.id)
        except UserIntegration.DoesNotExist:
            return HttpResponse("It seems the account you are looking for is deleted. If not try integrating again"
                                + " or contact the YellowAnt team")

        to_send = {'api_token': cw.api_token,
                   'api_secret': cw.api_secret,
                   'api_region': cw.api_region,
                   'webhook_url':cw.webhook_url
                   }
        # print json.dumps(to_send)
        return HttpResponse(json.dumps(to_send), content_type="application/json")
    else:
        redirect_url = "/market/applications/{}/accounts".format(settings.YA_APP_ID)
        return render(request, 'yellowant_generic.html',
                      {
                          'message_code': 405,
                          'message_text': "This seems to be an invalid request. If you think this isn't a mistake, please contact YellowAnt",
                          'return_url': redirect_url,
                          'return_url_text': "Back to Accounts",
                          'message_type': 0
                      },
                      status=405, )



def deleteaccount(request):
    if request.method == 'POST':
        # form= deleteForm(data = json.loads(request.body))
        data = json.loads(request.body)
        integration_id = data['integration_id']
        try:
            jenkins = UserIntegration.objects.get(yellowant_integration_id = integration_id, yellowant_user_id=request.user.id)
        except UserIntegration.DoesNotExist:
            data = {'message': "It seems the account you are looking for is deleted. If not, try integrating again"
                               + " or contact YellowAnt team"}
            return HttpResponse(json.dumps(data))

        yellowant_user = YellowAnt(access_token=jenkins.yellowant_user_token)
        try:
            a = yellowant_user.delete_user_integration(id=integration_id)

        except Exception as e:
            if e.error_code == 404:
                jenkins.delete()
                return HttpResponse(json.dumps({'status': True,
                                                'message': 'Your Account was deleted '
                                                        +' But it looked like you had already deleted it from Yellowant'
                                                        +" console"}))
            else:
                return HttpResponse(json.dumps({'status': False,
                                                'message': 'Something went wrong. Please contact YellowAnt team for the assist'}))

        jenkins.delete()
        return HttpResponse(json.dumps({'status': True,
                                        'message':'Your Account was deleted'}))
    else:
        redirect_url = "/market/applications/{}/accounts".format(settings.YA_APP_ID)
        return render(request, 'yellowant_generic.html',
                      {
                          'message_code': 405,
                          'message_text': "This seems to be an invalid request. If you think this isn't a mistake, please contact YellowAnt",
                          'return_url': redirect_url,
                          'return_url_text': "Back",
                          'message_type': 0
                      },
                      status=405, )



def index(request):
    if request.user.is_authenticated:
        print("abcd")
        return render(request, 'web/base.html')
    else:
        return render(request, 'web/login.html')
"""
def index(request,path):
    context = {
        "user_integrations": []
    }

    if request.user.is_authenticated:
        user_integrations = UserIntegration.objects.filter(user=request.user)
        #print(user_integration)
        for user_integration in user_integrations:
            context["user_integrations"].append(user_integration)
    #print("test2")
    return render(request, "home.html", context)

def userdetails(request):
    print("in userdetails")
    user_integrations_list = []
    if request.user.is_authenticated:
        user_integrations = UserIntegration.objects.filter(user=request.user)
        for user_integration in user_integrations:
            try:
                smut = awsec2.objects.get(yellowant_integration_invoke_name = user_integration.yellowant_integration_invoke_name)
                user_integrations_list.append({"user_invoke_name":user_integration.yellowant_integration_invoke_name, "id":user_integration.id, "app_authenticated":True,"is_valid":smut.AWS_update_login_flag})
            except UserIntegration.DoesNotExist:
                user_integrations_list.append({"user_invoke_name":user_integration.yellowant_integration_invoke_name, "id":user_integration.id, "app_authenticated":False})
    return HttpResponse(json.dumps(user_integrations_list), content_type="application/json")

def delete_integration(request, id=None):

        print("In delete_integration")
        print(id)
        access_token_dict = UserIntegration.objects.get(id=id)
        access_token = access_token_dict.yellowant_integration_token
        user_integration_id = access_token_dict.yellowant_integration_id
        print(user_integration_id)
        url = "https://api.yellowant.com/api/user/integration/%s" % (user_integration_id)
        yellowant_user = YellowAnt(access_token=access_token)
        yellowant_user.delete_user_integration(id=user_integration_id)
        response_json = UserIntegration.objects.get(yellowant_integration_token=access_token).delete()
        print(response_json)
        return HttpResponse("successResponse", status=200)


def view_integration(request, id=None):
    print("In view_integration")
    print(id)
    access_token_dict = UserIntegration.objects.get(id=id)
    access_token = access_token_dict.yellowant_integration_token
    user_integration_id = access_token_dict.yellowant_integration_id
    print(user_integration_id)
    url = "https://api.yellowant.com/api/user/integration/%s" % (user_integration_id)
    yellowant_user = YellowAnt(access_token=access_token)
    yellowant_user.delete_user_integration(id=user_integration_id)
    print(response_json)
    return HttpResponse("successResponse", status=200)