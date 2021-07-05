from django.db import models
from django.db.models import fields
from rest_framework import serializers
from .models import portfolio, transact


class transactSerializer(serializers.ModelSerializer):
    class Meta:
        model = transact
        fields = ['id','name','ticker','quantity','price','type']



class portfolioserializer(serializers.ModelSerializer):
   
    class Meta:
        model=portfolio
        fields = ['ticker','avg_buy_price','share']
   




