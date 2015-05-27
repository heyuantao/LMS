#-*-coding:utf-8-*-
from EXPS.models import Exp_Model, Exp_Arangement_Model,Location_Model
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http.response import HttpResponse
from django.views.generic.base import View
from django.core.context_processors import request
from rest_framework.renderers import JSONRenderer

class JSONResponse(HttpResponse):
    def __init__(self,data,**kwargs):
        content=JSONRenderer().render(data)      
        kwargs['content_type']='application/json'
        super(JSONResponse,self).__init__(content,**kwargs)        

class Exp_List(View):
    def get(self,request):
        exp_list=Exp_Model.objects.all()
        exp_list_dic=[Exp_Detail.a_queryset_item_to_dic(exp) for exp in exp_list]
        return JSONResponse(exp_list_dic);
    
class Exp_Detail(View):
    @classmethod
    def convert_need_assistant(cls,status):
        if status==False:
            return u"不需要值班助理"
        else:
            return u"需要值班助理"
    @classmethod
    def a_queryset_item_to_dic(cls,exp):
        exp_dic={'pk':exp.id,'user':exp.user.username,\
                       'exp_name':exp.exp_name,'theory_class':exp.theory_class,\
                       'student_grade':exp.student_grade,'student_subject':exp.student_subject,\
                       'student_num':exp.student_num,'teachers':exp.teachers,\
                       'exp_type_name':exp.exp_type.name,\
                       'exp_type_id':exp.exp_type.id,\
                       'need_assistant':cls.convert_need_assistant(exp.need_assistant),\
                       'other_info':exp.other_info}
        return exp_dic
    def get(self,request,exp_id):
        try:
            exp=Exp_Model.objects.get(pk=exp_id)
        except Exp_Model.DoesNotExist:
            raise Http404
        return JSONResponse(Exp_Detail.a_queryset_item_to_dic(exp))

class Exp_Arangement_List(View):
    def get(self,request):
        arangement_list=Exp_Arangement_Model.objects.all()
        arangement_list_dic=[Exp_Arangement_Detail.a_queryset_item_to_dic(arangement)\
                             for arangement in arangement_list]
        return JSONResponse(arangement_list_dic)
    
class Exp_Arangement_Detail(View):
    @classmethod
    def a_queryset_item_to_dic(cls,arangement):
        arangement_dic={"pk":arangement.id,\
                        "exp_name":arangement.exp_name.exp_name,\
                        "exp_id":arangement.exp_name.id,\
                        "week_order_name":arangement.week_order.name,\
                        "week_order_id":arangement.week_order.id,\
                        "week_name":arangement.week.name,\
                        "week_id":arangement.week.id,\
                        "time_order_name":arangement.time_order.name,\
                        "time_order_id":arangement.time_order.id,\
                        "item_name":arangement.item_name,\
                        "location_name":arangement.location.name,\
                        "location_id":arangement.location.id}
        return arangement_dic
    def get(self,request,arangement_id):
        try:
            arangement=Exp_Arangement_Model.objects.get(pk=arangement_id)
        except Exp_Arangement_Model.DoesNotExist:
            raise Http404
        return JSONResponse(Exp_Arangement_Detail.a_queryset_item_to_dic(arangement))

class Location_List(View):
    def get(self,request):
        location_list=Location_Model.objects.all().exclude(name=u'未选择')
        location_list_dic=[Location_Detail.a_queryset_item_to_dic(location) \
                           for location in location_list]
        return JSONResponse(location_list_dic)
    
class Location_Detail(View):
    @classmethod
    def a_queryset_item_to_dic(cls,location):
        location_dic={"location_name":location.name,"pk":location.id,"location_abbr":location.abbr}
        return location_dic
    def get(self,request,location_id):
        try:
            location=Location_Model.objects.get(pk=location_id)
        except Location_Model.DoesNotExist:
            raise Http404
        location_dic=Location_Detail.a_queryset_item_to_dic(location)
        return JSONResponse(location_dic)
'''
class Exp_List(APIView):
    def get(self,request,format=None):
        exps=Exp_Model.objects.all()
        exp_ser=Exp_Model_Serializer(exps,many=True)
        return Response(exp_ser.data)

class Exp_Detail(APIView):
    def get_object(self,id):
        try:
            exp=Exp_Model.objects.get(pk=id)
            return exp
        except Exp_Model.DoesNotExist:
            raise Http404
    def get(self,request,id,format=None):
        exp=self.get_object(id)
        exp_ser=Exp_Model_Serializer(exp)
        return Response(exp_ser.data)
    
class Exp_Arangement_List(APIView):
    def get(self,request,format=None):
        aranges=Exp_Arangement_Model.objects.all()
        aranges_ser=Exp_Arangement_Model_Serializer(aranges,many=True)
        return Response(aranges_ser.data)
class Exp_Arangement_Detail(APIView):
    def get_obj(self,id):
        try:
            arangement=Exp_Arangement_Model.objects.get(pk=id)
            return arangement
        except Exp_Arangement_Model.DoesNotExist:
            raise Http404
    def get(self,request,id,format=None):
        arangement=self.get_obj(id)
        arangement_ser=Exp_Arangement_Model_Serializer(arangement)
        return Response(arangement_ser.data)
        
    '''