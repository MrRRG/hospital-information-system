from django.urls import path

from . import views

urlpatterns = [
    path("", views.visit_list, name="visit_list"),
    path("new/", views.visit_create, name="visit_create"),
    path("<int:pk>/", views.visit_detail, name="visit_detail"),
    path("<int:pk>/edit/", views.visit_edit, name="visit_edit"),
]
