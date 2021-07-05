from django.db import models
from django.core.validators import MinValueValidator


# Create your models here.

class portfolio(models.Model):
    ticker=models.CharField(primary_key=True,max_length=100)
    avg_buy_price=models.FloatField()
    share=models.PositiveIntegerField()
    
    
class transact(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=200,null=False)
    ticker=models.CharField(max_length=200,null=False)
    quantity=models.PositiveIntegerField(null=False,validators=[MinValueValidator(1)])
    price=models.PositiveIntegerField(null=False)
    type=models.CharField(max_length=200,null=False,choices=[("buy","buy"),("sell","sell")])



    
