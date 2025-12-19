from ticket import models

import requests
import json
import pandas as pd

####################################### POST Method #######################################
def post(*args, **kwargs):
    url = kwargs['url']
    header = None
    data = None
    if kwargs['type'] == "authorization_code":
        data={
            "code" : "1000.2beca3219974d4b40a23c1282e696cfc.177dcb8a3054fb62effffb6f0572985d",
            "client_id" : kwargs['client_id'],
            "client_secret" : kwargs['client_secret'],
            "grant_type" : kwargs['type'], 
            "redirect_uri" : "https://desk.zoho.in/"
        }
    if kwargs['type'] == "refresh_token":
        data={
            "refresh_token" : kwargs['refreshtoken'], 
            "client_id" : kwargs['client_id'],
            "client_secret" : kwargs['client_secret'],
            "grant_type" : kwargs['type'], 
            "redirect_uri" : "https://desk.zoho.in/"
        }
    if kwargs['type'] == "move_ticket":
        header = {
            "orgId" : kwargs['org_id'],
            "Authorization" : f'Zoho-oauthtoken {kwargs['access_token']}'
        }
        data = kwargs['param']
        
    try:
        if kwargs['type'] != "move_ticket":
            resp = requests.post(url, data=data, headers=header)
            try:
                json_resp = resp.json()
            except:
                json_resp = json.loads(resp.text)

        elif kwargs['type'] == "move_ticket":
            resp = requests.post(url, json=data, headers=header)
            json_resp = resp.status_code

        return json_resp
    except Exception as e:
        return e
    
####################################### GET Method #######################################
def get(**kwargs):
    url = kwargs['url']
    if kwargs['type'] == "search":
        header={
            "orgId" : kwargs['org_id'],
            "Authorization" : f'Zoho-oauthtoken {kwargs['access_token']}'
        }
    try:
        resp = requests.get(url, headers=header)
        try:
            json_resp = resp.json()
        except:
            json_resp = json.loads(resp.text)

        return json_resp
    except Exception as e:
        return e
    
####################################### UPDATE Method #######################################
def update(**kwargs):
    url = kwargs['url']
    header={
        "orgId" : kwargs['org_id'],
        "Authorization" : f'Zoho-oauthtoken {kwargs['access_token']}'
    }
    try:
        resp = requests.patch(url, json=kwargs['data'] , headers=header)
        try:
            json_resp = resp.json()
        except:
            json_resp = json.loads(resp.text)

        return json_resp
    except Exception as e:
        return e

####################################### Extract CSV #######################################
def extract_csv(file_url, start, type, user):
    op = None
    if type == 'department':
        dframe = pd.read_csv(file_url)
        op = dframe
        return op

    if type == 'ticket_move' :
        dframe = pd.read_csv(file_url, dtype={"Search Message" : "string","Move Message" : "string","Update Message" : "string"})
        oauth_obj = models.OauthModel.objects.filter(user=user, status="Active").first()
        if not oauth_obj:
            return "No record found"
            
        chunck_size = 2
        while start < len(dframe):
            end = start + chunck_size
            batch = dframe[start:end]
            # if any colunm have value, ignore for already processed
            mask = batch[["Search Message", "Move Message", "Update Message"]].replace("", pd.NA).notna().any(axis=1)
            filter_batch = batch[mask==False]
            for index, col in filter_batch.iterrows():
                
                nmg_dept_obj = models.NMGDepartmentModel.objects.filter(oauthModal=oauth_obj, departmentid=col['Department']).first()
                if nmg_dept_obj:
                    zen_dept_obj = models.ZenDepartmentModel.objects.filter(oauthModal=oauth_obj, depatment_name=nmg_dept_obj.depatment_name).first()
                    if zen_dept_obj:
                        search_ticket_resp = get(url = f"https://desk.zoho.in/api/v1/tickets/search?subject={col['Subject']}", org_id = oauth_obj.orgId, access_token = oauth_obj.access_token, type="search")
                        
                        if not any (err in search_ticket_resp for err in ("errorCode", "error")):
                            search_data = search_ticket_resp['data']
                            for loop_obj in search_data:
                               
                                if zen_dept_obj.departmentid != loop_obj["departmentId"]:
                                    try:
                                        qury = {"departmentId" : zen_dept_obj.departmentid}
                                        moveTicket_resp = post(url = f"https://desk.zoho.in/api/v1/tickets/{loop_obj['id']}/move", org_id = oauth_obj.orgId , access_token = oauth_obj.access_token, param = qury, type="move_ticket")
                                        if moveTicket_resp == 200:
                                            update_data = {
                                                "status" : loop_obj["status"],
                                                "dueDate" : loop_obj["dueDate"],
                                                "closedTime" : loop_obj["closedTime"],
                                                "assigneeId"  : loop_obj["assigneeId"],  
                                            }
                                            update_ticket = update(url = f"https://desk.zoho.in/api/v1/tickets/{loop_obj['id']}", org_id = oauth_obj.orgId, access_token = oauth_obj.access_token, data = update_data)
                                            batch.at[index,"Update Message"] = str(update_ticket)
                                            op = "Updated"
                                        else:
                                            batch.at[index,"Move Message"] = str(moveTicket_resp)
                                            op = batch.at[index,"Move Message"]
                                    except Exception as e:
                                        batch.at[index,"Move Message"] = str(e)
                                        op = batch.at[index,"Move Message"]
                                else:
                                    batch.at[index,"Search Message"] = "Already department same"
                                    op = batch.at[index,"Search Message"]
                                    
                                break
                        else:
                            batch.at[index,"Search Message"] = str(search_ticket_resp)
                            op = batch.at[index,"Search Message"]
                    else:
                        op = "No Zen Department match"
                else:
                    op = "No NMG Department match"
            start = end
            break
        dframe.to_csv(file_url, index=False)
   
    return op

