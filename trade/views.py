import re
from django.core import exceptions
from django.db import IntegrityError
from django.db.models import query
from django.db.models.aggregates import Sum
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, request, response
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from .models import transact,portfolio
from .serializers import transactSerializer,portfolioserializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import copy
from rest_framework.response import Response
# Create your views here.

@api_view(['GET'])
def apiOverview(request):               #index page of API to provide details about paths/routes
    api_urls={
        'View All Trades':"/trade/",
        'Select Trade':"/trade/<int:pk>",
        'Add New Trade':"/trade-add/",
        'Delete Trade':'trade-delete/<int:pk>',
        'Update Trade':'trade-update/<int:pk>',
        'Show Portfolio':'/portfolio/',
        'Returns on Invenstment':'/returns/',
    }
    return Response(api_urls)

@api_view(['GET'])
def tradedetails(request):                          #fetching all data from table 
    if(request.method=='GET'):
        data=transact.objects.all()                    #data holds data from table in querryset format
        serial=transactSerializer(data,many=True)      #converting querryset in dict fromat
        return Response(serial.data,status=200)
@csrf_exempt
@api_view(['POST'])
def addtrades(request):
    try:
        if(request.method=='POST'):
            serial=transactSerializer(data=request.data)
            #print(request.data['id'])
            if serial.is_valid()==True:                          #checking if serialized data is matching model's schema                                      
                s=request.data
            
                #this code is responsible to manage portfolio after each new trade    
                if(portfolio.objects.filter(ticker=s['ticker']).exists()):    #if portfolio has existing entry than change it
                    current_portfolio=portfolio.objects.get(ticker=s['ticker'])

                    if(s['type']=='buy'):                                     #buying new share will affect average buy price
                        current_portfolio.avg_buy_price=((current_portfolio.avg_buy_price)*current_portfolio.share+(s['price']*s['quantity']))/(current_portfolio.share+s['quantity'])
                        current_portfolio.share=current_portfolio.share+s['quantity']
                        tmp=portfolio.objects.filter(ticker=s['ticker']).update(avg_buy_price=current_portfolio.avg_buy_price,share=current_portfolio.share)

                    elif(s['type']=='sell' and s['quantity'] < current_portfolio.share): #check if selling count is less than equal to holding count
                        current_portfolio.share=current_portfolio.share-s['quantity']
                        print(current_portfolio.avg_buy_price,current_portfolio.share)
                        tmp=portfolio.objects.filter(ticker=s['ticker']).update(share=current_portfolio.share)

                    elif(current_portfolio.share - s['quantity']==0):   #if after selling share portfolio will hold 0 share then delete entry
                            current_portfolio.delete()
                    else:
                        return Response("number of selling share is more than holding")
                    serial.save()

                elif(s['type']=='sell'):
                    return Response("can not sale share if portfolio dosent hold any")

                else:                               #if portfolio has no entry than create new
                    obj={"ticker":s['ticker'],
                        "avg_buy_price":s['price'],
                        "share":s['quantity']}
                    newrow=portfolioserializer(data=obj)
                    serial.save()
                    if newrow.is_valid()==True:
                        newrow.save()
                    else:
                        return Response(serial.errors)
                return Response(serial.data)
            else:
                return Response(serial.errors)
    except Exception as e:
        return Response(f"{e}")
    

@api_view(['GET'])
def singletradedetails(request,index):
    if(request.method=='GET'):
        try:
            data=transact.objects.get(pk=index)
            serial=transactSerializer(data)
            return Response(serial.data)
        except Exception as e:
            return Response(f"{e}")


@api_view(['PUT'])
def tradeupdate(request,index):
    if(request.method=='PUT'):
        try:
            dataset=transact.objects.get(pk=index)
            serial=transactSerializer(instance=dataset,data=request.data)
            if serial.is_valid()==True:
                current_portfolio=portfolio.objects.get(ticker=dataset.ticker)      #get relevent portfolio data
                backup=copy.deepcopy(current_portfolio)
                if dataset.type=="sell":
                    current_portfolio.share=current_portfolio.share+dataset.quantity    #revert back the selling trade
                    current_portfolio.save() 
                if dataset.type=="buy":
                    if(current_portfolio.share - dataset.quantity==0):   #if after deleting trade portfolio will hold 0 share then delete entry
                        current_portfolio.delete()
                    else:
                        current_portfolio.avg_buy_price=((current_portfolio.avg_buy_price)*current_portfolio.share - (dataset.price * dataset.quantity))/(current_portfolio.share - dataset.quantity)
                        current_portfolio.share=current_portfolio.share - dataset.quantity
                        current_portfolio.save()
                
                s=request.data
                if(portfolio.objects.filter(ticker=s['ticker']).exists()):    #if portfolio has existing entry than change it
                    current_portfolio=portfolio.objects.get(ticker=s['ticker'])

                    if(s['type']=='buy'):                                     #buying new share will affect average buy price
                        current_portfolio.avg_buy_price=((current_portfolio.avg_buy_price)*current_portfolio.share+(s['price']*s['quantity']))/(current_portfolio.share+s['quantity'])
                        current_portfolio.share=current_portfolio.share+s['quantity']
                        tmp=portfolio.objects.filter(ticker=s['ticker']).update(avg_buy_price=current_portfolio.avg_buy_price,share=current_portfolio.share)

                    elif(s['type']=='sell' and s['quantity'] < current_portfolio.share): #check if selling count is less than equal to holding count
                        current_portfolio.share=current_portfolio.share-s['quantity']
                        print(current_portfolio.avg_buy_price,current_portfolio.share)
                        tmp=portfolio.objects.filter(ticker=s['ticker']).update(share=current_portfolio.share)

                    elif(current_portfolio.share - s['quantity']==0):   #if after selling share portfolio will hold 0 share then delete entry
                            current_portfolio.delete()
                    else:
                        backup.save()
                        return Response("number of selling share is more than holding")
                    serial.save()

                elif(s['type']=='sell'):
                    backup.save()
                    print(backup.ticker)
                    return Response("can not sale share if portfolio dosent hold any")
                
                else:                               #if portfolio has no entry than create new
                    obj={"ticker":s['ticker'],
                        "avg_buy_price":s['price'],
                        "share":s['quantity']}
                    newrow=portfolioserializer(data=obj)
                    serial.save()
                    if newrow.is_valid()==True:
                        newrow.save()
                    else:
                        return Response(serial.errors)
                return Response(serial.data)

            else:
                return Response(serial.errors)

        
        except Exception as e:
            return Response(f"{e}")

@api_view(['Delete'])
def tradedelete(request,index):
    try:
        dataset=transact.objects.get(pk=index)          #select the trade which needs to be deleted
        tmp=transactSerializer(dataset)
        deltrade=tmp.data
        current_portfolio=portfolio.objects.get(ticker=deltrade['ticker'])      #get relevent portfolio data
        if deltrade['type']=="sell":
            current_portfolio.share=current_portfolio.share+deltrade['quantity']    #revert back the selling trade 
        if deltrade['type']=='buy':
            if(current_portfolio.share - deltrade['quantity']==0):   #if after deleting trade portfolio will hold 0 share then delete entry
                current_portfolio.delete()
            else:
                current_portfolio.avg_buy_price=((current_portfolio.avg_buy_price)*current_portfolio.share - (deltrade['price'] * deltrade['quantity']))/(current_portfolio.share - deltrade['quantity'])
                current_portfolio.share=current_portfolio.share - deltrade['quantity']
        current_portfolio.save()
        dataset.delete()
        return Response("Selected Item is Deleted Sucessfully")
    except Exception as e:
        return Response(f"{e}")



@api_view(['GET'])
def showportfolio(request):
    try:
        data=portfolio.objects.all()
        serial=portfolioserializer(data,many=True)
        return Response(serial.data)
    except Exception as e:
        return Response(f"{e}")

@api_view(['GET'])
def roi(request):
    if(request.method=='GET'):
        try:
            dataset=portfolio.objects.all()
            serial=portfolioserializer(dataset,many=True)
            sum=0
            current_price=100
            for i in serial.data:
                sum=sum+((current_price-i['avg_buy_price'])*i['share'])
            #print(sum)
            obj={'Returns':sum}
            return Response(obj)
        except Exception as e:
            return Response(f"{e}")


def is_same(first,second):
    for i,j in first.items(),second.items():
        if(not i==j):
            return False
    else:
        return True

