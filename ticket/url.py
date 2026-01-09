from django.urls import path
from ticket import views

urlpatterns = [
    path('test', views.test, name="test"),
    path('refres_token', views.refreshToken, name='refreshToken'),
    path('department', views.departments, name='department'),
    path('updatedept',views.updateDepartment, name='updatedept'),
    # path('updatedeptnew',views.updateDepartmentNew, name='updatedeptnew'),
    # path('updatedeptnew1',views.updateDepartmentNew1, name='updatedeptnew1'),
]
