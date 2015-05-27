#-*-coding:utf-8-*-
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Week_Model(models.Model):
    name=models.CharField(max_length=20)
    abbr=models.IntegerField()
    def __unicode__(self):
        return "%s------%s" %(self.name,self.abbr)
class Week_Order_Model(models.Model):
    name=models.CharField(max_length=20)
    abbr=models.IntegerField()
    def __unicode__(self):
        return "%s------%s" %(self.name,self.abbr)
class Time_Order_Model(models.Model):
    name=models.CharField(max_length=20)
    abbr=models.IntegerField()
    def __unicode__(self):
        return "%s------%s" %(self.name,self.abbr)
class Location_Model(models.Model):
    name=models.CharField(max_length=20)
    abbr=models.IntegerField()
    def __unicode__(self):
        return "%s------%s" %(self.name,self.abbr)  
class Exp_Type_Model(models.Model):
    name=models.CharField(max_length=20)
    abbr=models.IntegerField()
    def __unicode__(self):
        return "%s------%s" %(self.name,self.abbr)

class Exp_Model(models.Model):
    user=models.ForeignKey(User)
    exp_name=models.CharField(max_length=40)
    theory_class=models.CharField(max_length=40)
    student_grade=models.CharField(max_length=40)
    student_subject=models.CharField(max_length=40)
    student_num=models.IntegerField()
    teachers=models.CharField(max_length=60)
    exp_type=models.ForeignKey(Exp_Type_Model)
    need_assistant=models.BooleanField(default=True)
    other_info=models.TextField(blank=True)
    #exp type special information begin
    exp_number_by_authority=models.IntegerField(default=0,blank=True)
    exp_time_by_authority=models.IntegerField(default=0,blank=True)
    exp_number_by_plan=models.IntegerField(default=0,blank=True)
    exp_time_by_plan=models.IntegerField(default=0,blank=True)
    #exp type special information end
    def __unicode__(self):
        return self.exp_name

class Exp_Arangement_Model(models.Model):
    exp_name=models.ForeignKey(Exp_Model)
    week_order=models.ForeignKey(Week_Order_Model)
    week=models.ForeignKey(Week_Model)
    time_order=models.ForeignKey(Time_Order_Model)
    item_name=models.CharField(max_length=80,blank=True)
    location=models.ForeignKey(Location_Model)
    def __unicode__(self):
        return self.exp_name
    
class System_Setting_Model(models.Model):
    key=models.CharField(max_length=50)
    value=models.TextField(blank=True)
    def __unicode__(self):
        return "%s----%s" %(self.key,self.value)
    