from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from ticket import functions, models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import os



nmgDept_uri = os.path.join(settings.BASE_DIR, "ticket/import", "NMG Departments.csv")
zenDept_uri = os.path.join(settings.BASE_DIR, "ticket/import", "Zen Department.csv")

# account_uri = os.path.join(settings.BASE_DIR, "ticket/import", "Accounting Tickets.csv")
# accountRecievable_uri = os.path.join(settings.BASE_DIR, "ticket/import", "Account Recievable.csv")
# Aristera_uri = os.path.join(settings.BASE_DIR, "ticket/import", "Aristera@NMG.CPA.csv")
# BusinessTax_uri = os.path.join(settings.BASE_DIR, "ticket/import", "Business Tax.csv")
# General URI is pending, it goes to all record is error. let me check
General_uri = os.path.join(settings.BASE_DIR, "ticket/import", "General Support.csv") 
# hr_uri = os.path.join(settings.BASE_DIR, "ticket/import", "HR Service.csv")
# incoporate_uri = os.path.join(settings.BASE_DIR, "ticket/import", "Incoporate.csv")
# laderal_uri = os.path.join(settings.BASE_DIR, "ticket/import", "Laderal.csv")
# medbeacon_uri = os.path.join(settings.BASE_DIR, "ticket/import", "MedBeacon.csv")
# onboarindg_uri = os.path.join(settings.BASE_DIR, "ticket/import", "Onboarding.csv")
# personaltax_uri = os.path.join(settings.BASE_DIR, "ticket/import", "PersonalTax.csv")
# portal_uri = os.path.join(settings.BASE_DIR, "ticket/import", "Portal.csv")
# salestax_uri = os.path.join(settings.BASE_DIR, "ticket/import", "SalesTax.csv")

# Completed - account_uri, Aristera_uri, BusinessTax_uri

# Create your views here.
def test(req):
    print(req.user.id)
    return JsonResponse({"message": "Okay"})

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
    # ticeket_resp = functions.extract_csv(accountRecievable_uri, 155, 'ticket_move', req.user)
    user_id = 1
    expiry_time = timezone.now() - timedelta(minutes=45)
    oauth_obj  = models.OauthModel.objects.filter(user=user_id, status="Active").first()
    
    if oauth_obj.updated_time < expiry_time:
        refresh_token = functions.post(url="https://accounts.zoho.in/oauth/v2/token", client_id = oauth_obj.client_id, client_secret = oauth_obj.secret_id, type="refresh_token", refreshtoken = oauth_obj.refresh_token)
        if 'error' not in refresh_token:
            oauth_obj.access_token =  refresh_token['access_token']
            oauth_obj.save(update_fields=["access_token", "updated_time"])
            print(f"Token refreshed for user = {oauth_obj.user}")
        else:
            print(f"refresh_token['error'] - {refresh_token}")          
    else:
        print("token already updated")
        print("Processing state----")
        schedule_obj, created = models.CsvSchedule.objects.get_or_create(
        oauthModal=oauth_obj,
        id=1,
        defaults={
            "name": "faiyas",
            "last_row": 0,
            "last_run": timezone.now(),
            "is_running": False
            }
        )
        if schedule_obj.last_run  < timezone.now():
            ticeket_resp = functions.extract_csv(General_uri, schedule_obj.last_row, 'ticket_move', user_id)
            schedule_obj.last_run = timezone.now() + timedelta(seconds=25)
            schedule_obj.last_row = schedule_obj.last_row + 10
            schedule_obj.save()
            print("Completed")
        else:
            print("get")
    
    return JsonResponse({"LastTime": schedule_obj.last_run, "LastRow": schedule_obj.last_row})

# def updateDepartmentNew(req):
#     user_id = 1
#     expiry_time = timezone.now() - timedelta(minutes=45)
#     oauth_obj  = models.OauthModel.objects.filter(user=user_id, status="Active").first()
    
#     if oauth_obj.updated_time < expiry_time:
#         refresh_token = functions.post(url="https://accounts.zoho.in/oauth/v2/token", client_id = oauth_obj.client_id, client_secret = oauth_obj.secret_id, type="refresh_token", refreshtoken = oauth_obj.refresh_token)
#         if 'error' not in refresh_token:
#             oauth_obj.access_token =  refresh_token['access_token']
#             oauth_obj.save(update_fields=["access_token", "updated_time"])
#             print(f"Token refreshed for user = {oauth_obj.user}")
#         else:
#             print(f"refresh_token['error'] - {refresh_token}")          
#     else:
#         print("new token already updated")
#         print("new Processing state----")
#         schedule_obj, created = models.CsvSchedule.objects.get_or_create(
#         oauthModal=oauth_obj,
#         id=2,
#         defaults={
#             "name": "Extra schedule",
#             "last_row": 0,
#             "last_run": timezone.now(),
#             "is_running": False
#             }
            
#         )
#         if schedule_obj.last_run  < timezone.now():
#             ticeket_resp = functions.extract_csv(salestax_uri, schedule_obj.last_row, 'ticket_move', user_id)
#             schedule_obj.last_run = timezone.now() + timedelta(seconds=30)
#             schedule_obj.last_row = schedule_obj.last_row + 10
#             schedule_obj.save()
#             print("Completed")
#         else:
#             print("get")
    
#     return JsonResponse({"LastTime": schedule_obj.last_run, "LastRow": schedule_obj.last_row})

# def updateDepartmentNew1(req):
#     user_id = 1
#     expiry_time = timezone.now() - timedelta(minutes=45)
#     oauth_obj  = models.OauthModel.objects.filter(user=user_id, status="Active").first()
    
#     if oauth_obj.updated_time < expiry_time:
#         refresh_token = functions.post(url="https://accounts.zoho.in/oauth/v2/token", client_id = oauth_obj.client_id, client_secret = oauth_obj.secret_id, type="refresh_token", refreshtoken = oauth_obj.refresh_token)
#         if 'error' not in refresh_token:
#             oauth_obj.access_token =  refresh_token['access_token']
#             oauth_obj.save(update_fields=["access_token", "updated_time"])
#             print(f"Token refreshed for user = {oauth_obj.user}")
#         else:
#             print(f"refresh_token['error'] - {refresh_token}")          
#     else:
#         print("new1 token already updated")
#         print("new1 Processing state----")
#         schedule_obj, created = models.CsvSchedule.objects.get_or_create(
#         oauthModal=oauth_obj,
#         id=3,
#         defaults={
#             "name": "Extra1 schedule",
#             "last_row": 0,
#             "last_run": timezone.now(),
#             "is_running": False
#             }
#         )
#         if schedule_obj.last_run  < timezone.now():
#             ticeket_resp = functions.extract_csv(General_uri, schedule_obj.last_row, 'ticket_move', user_id)
#             schedule_obj.last_run = timezone.now() + timedelta(seconds=30)
#             schedule_obj.last_row = schedule_obj.last_row + 10
#             schedule_obj.save()
#             print("Completed")
#         else:
#             print("get")
    
#     return JsonResponse({"LastTime": schedule_obj.last_run, "LastRow": schedule_obj.last_row})