from django.contrib import admin
from ticket.models import OauthModel, NMGDepartmentModel, ZenDepartmentModel, CsvSchedule
# Register your models here.

@admin.register(OauthModel)
class OauthModelAdmin(admin.ModelAdmin):
    list_display  = ("user", "client_id", "secret_id", "refresh_token" ,"access_token", "create_time", "updated_time")
    search_fields = ["User__username"]
    readonly_fields = ["access_token"]

@admin.register(NMGDepartmentModel)
class NMGDepartmentModelAdmin(admin.ModelAdmin):
    list_display  = ("oauthModal__user__username", "departmentid", "depatment_name", "create_time", "updated_time")
    search_fields = ["oauthModal__user__username"]

@admin.register(ZenDepartmentModel)
class ZenDepartmentModelAdmin(admin.ModelAdmin):
    list_display  = ("oauthModal__user__username", "departmentid", "depatment_name", "create_time", "updated_time")
    search_fields = ["oauthModal__user__username"]

@admin.register(CsvSchedule)
class CsvScheduleModelAdmin(admin.ModelAdmin):
    list_display  = ("name", "last_row", "last_run", "is_running")
    search_fields = ["name", "last_run"]