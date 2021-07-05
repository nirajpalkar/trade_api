from django.urls import path
from . import views

urlpatterns = [
    path('',views.apiOverview),
    path('portfolio/',views.showportfolio),
    path('returns/',views.roi),
    path('trade/',views.tradedetails),
    path('trade/<int:index>',views.singletradedetails),
    path('trade-update/<int:index>',views.tradeupdate),
    path('trade-delete/<int:index>',views.tradedelete),
    path('trade-add/',views.addtrades),



]