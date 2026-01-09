from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from ticket.models import OauthModel
from django.http import JsonResponse
from ticket import functions

class Command(BaseCommand):
    help = "Refresh OAuth tokens if expired"

    def handle(self, *args, **kwargs):
        self.stdout.write("TOKEN REFRESH COMMAND STARTED")
        expiry_time = timezone.now() - timedelta(minutes=45)

        tokens = OauthModel.objects.filter(
            status="Active",
            updated_time__lte=expiry_time
        )
        self.stdout.write("TOKEN REFRESH - ", tokens)
        for token in tokens:
            print(f"Refreshing token for {token.user}")
            refresh_token = functions.post(url="https://accounts.zoho.in/oauth/v2/token", client_id = token.client_id, client_secret = token.secret_id, type="refresh_token", refreshtoken = token.refresh_token)
            if 'error' not in refresh_token:
                token.access_token =  refresh_token['access_token']
                token.save(update_fields=["access_token", "updated_time"])
                print(f"Token refreshed for user = {token.user}")
            else:
                print(f"refresh_token['error'] - {refresh_token}")          
