from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from ticket import functions
from ticket import models
from django.conf import settings
import os


nmgDept_uri = os.path.join(settings.BASE_DIR, "ticket/import", "NMG Departments.csv")
zenDept_uri = os.path.join(settings.BASE_DIR, "ticket/import", "Zen Department.csv")
account_uri = os.path.join(settings.BASE_DIR, "ticket/import", "Accounting Tickets.csv")
# Create your views here.

# Test
from django.utils import timezone
from datetime import timedelta

def test(req):
    # print(timezone.localtime(timezone.now()))
    # print(timedelta(minutes=45))
    # oa = models.OauthModel.objects.filter(user=req.user, status="Active").first()
    # oa.save()
    # models.OauthModel.objects.filter(user=req.user, status="Active").update(updated_time=timezone.now())
    return HttpResponse("s")

####################################### Generate Oauth code #######################################
def oauth():
    oauth_code = functions.post(url="https://accounts.zoho.in/oauth/v2/token", client_id = CLIENT_ID, client_secret = CLIENT_SECRET, type="authorization_code")
    if 'error' not in oauth_code:
        print(f'oauth_code - {oauth_code}')
    else:
        print(f'oauth_code errr - {oauth_code['error']}')
# print("Refresh Token - ",oauth())

####################################### Refresh Token #######################################
def refreshToken(request):
    oauth_obj = models.OauthModel.objects.filter(user=request.user, status="Active").first()
    if not oauth_obj:
        return HttpResponse("<p>Access Token - No record found</p>")
    refresh_token = functions.post(url="https://accounts.zoho.in/oauth/v2/token", client_id = oauth_obj.client_id, client_secret = oauth_obj.secret_id, type="refresh_token", refreshtoken = oauth_obj.refresh_token)
    if 'error' not in refresh_token:
        oauth_obj.access_token =  refresh_token['access_token']
        oauth_obj.save()
    else:
        print(refresh_token['error'])
    return HttpResponse(f"<p>Access Token - {refresh_token['access_token']}</p>")

####################################### import Departments #######################################
def departments(request):
    oauth_obj = models.OauthModel.objects.filter(user=request.user, status="Active").first()
    if not oauth_obj:
        print("No record found")

    nmg_data = functions.extract_csv(nmgDept_uri, 0 , 'department', request.user)
    for index, col in nmg_data.iterrows():
        models.NMGDepartmentModel.objects.update_or_create(oauthModal=oauth_obj, departmentid=col["departmentid"], defaults={"depatment_name":col["depatment_name"]}) 
        print("NMG create")
    
    zen_data = functions.extract_csv(zenDept_uri, 0 , 'department', request.user)
    for inx, zcol in zen_data.iterrows():
        models.ZenDepartmentModel.objects.update_or_create(oauthModal=oauth_obj, departmentid=zcol["departmentid"], defaults={"depatment_name" : zcol["depatment_name"]})
        print("Zen create")

    nmgList = list(models.NMGDepartmentModel.objects.filter(oauthModal=oauth_obj).values_list("depatment_name", flat=True))
    zenList = list(models.ZenDepartmentModel.objects.filter(oauthModal=oauth_obj).values_list("depatment_name", flat=True))
    html = f"<p>NMG Department - {nmgList}</p><br><br><p>Zen Department - {zenList}</p>"

    return HttpResponse(html)

####################################### Update Ticket Department #######################################
def updateDepartment(req):
    ticeket_resp = functions.extract_csv(account_uri, 0, 'ticket_move', req.user)
    print("ticeket_resp - ", ticeket_resp)
    return HttpResponse(ticeket_resp)
