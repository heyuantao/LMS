#-*-coding:utf-8-*-
from django.db import models
from django.contrib.auth.models import User
from EXPS.models import Exp_Model,Week_Order_Model,Week_Model,Time_Order_Model,Location_Model
# Create your models here.
class Student_Assistant_Model(models.Model):
    username=models.CharField(max_length=40)
    phone=models.CharField(max_length=40)
    email=models.CharField(max_length=40)
    def __unicode__(self):
        return "%s----%s" %(self.username,self.email)
    
class Student_Assistant_Arange_Model(models.Model):
    week_order=models.ForeignKey(Week_Order_Model)
    week=models.ForeignKey(Week_Model)
    time_order=models.ForeignKey(Time_Order_Model)
    student=models.ForeignKey(Student_Assistant_Model)
    def __unicode__(self):
        return "%s--%s--%s" %(self.week_order.name,self.week.name,self.time_order.name)