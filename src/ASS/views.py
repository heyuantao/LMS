#-*-coding:utf-8-*-
from EXPS.models import Exp_Model, Exp_Arangement_Model, Exp_Type_Model,\
    Week_Model, Week_Order_Model, Time_Order_Model, Location_Model,\
    System_Setting_Model
from ASS.models import Student_Assistant_Arange_Model,Student_Assistant_Model
from django.shortcuts import render,render_to_response
from django.views.generic.base import View
from django.contrib import auth
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.files import File
from EXPS.forms import UploadFileForm
from django.template.context import RequestContext
from datetime import date,timedelta
from django.utils import timezone
from xlwt import easyxf
import pickle
import xlrd,xlwt
import os
from django.contrib.auth.decorators import login_required
from EXPS.decorator import is_login,can_change_aranges_or_exp,\
    can_change_student_assistant
from EXPS.views import System_Setting

class Show_Student_Assistant(View):
    template='show_student_assistant.html'
    def get(self,request):
        students=Student_Assistant_Model.objects.all().exclude(username=u'未选择')
        return render_to_response(self.template,{'students':students},RequestContext(request))
    def post(self,request):
        messages.warning(request, u'不支持该操作')
        return HttpResponseRedirect(reverse('error_page'))
class Show_Assistant_Recent_Aranges(View):
    recent_template='show_assistant_recent_arange.html'
    def get(self,request,ass_id=''):
        current_week_order_abbr=System_Setting.current_week_order_abbr()
        next_week_order_abbr=System_Setting.next_week_order_abbr()
        #print current_week_order_abbr,next_week_order_abbr
        #tomorrow_week_order_abbr,tomorrow_week_abbr=System_Setting.tomorrow_week_order_and_week_abbr()
        #print tomorrow_week_order_abbr,tomorrow_week_abbr
        assistant=Student_Assistant_Model.objects.get(pk=ass_id)
        current_week_order_assistant_aranges=Student_Assistant_Arange_Model.objects.filter(student=assistant,week_order__abbr=current_week_order_abbr).order_by('week_order','week','time_order')
        next_week_order_assistant_aranges=Student_Assistant_Arange_Model.objects.filter(student=assistant,week_order__abbr=next_week_order_abbr).order_by('week_order','week','time_order')
        return render_to_response(self.recent_template,{'assistant':assistant,'current_week_order_assistant_aranges':current_week_order_assistant_aranges,'next_week_order_assistant_aranges':next_week_order_assistant_aranges},RequestContext(request))
    def post(self,request,ass_id=''):
        messages.warning(request,u'不支持该操作')
        return HttpResponseRedirect(reverse('error_page'))
class Student_Assistant_Edit(View):
    show_with_edit_and_add_template='show_student_assistant_with_edit_and_add.html'
    edit_template='edit_student_assistant.html'
    add_template='add_student_assistant.html'
    def get_edit_assistant(self,request,ass_id,todo):
        try:
            student=Student_Assistant_Model.objects.get(pk=ass_id)
            return render_to_response(self.edit_template,{'student':student},RequestContext(request))
        except Student_Assistant_Model.DoesNotExist:
            messages.warning(request,u'操作错误')
            return HttpResponseRedirect(reverse('error_page'))
    def get_add_assistant(self,request,ass_id,todo):
        return render_to_response(self.add_template,{},RequestContext(request))
    def get_delete_assistant(self,request,ass_id,todo):
        try:
            student=Student_Assistant_Model.objects.get(pk=ass_id)
            arange_count=Student_Assistant_Arange_Model.objects.filter(student=student).count()
            if arange_count>0:
                msg=u'该助理有%s次值班安排，不能直接删除' %(arange_count)
                messages.warning(request,msg)
                return HttpResponseRedirect(reverse('error_page'))
            student.delete()
            return HttpResponseRedirect(reverse('assistant_edit_and_add'))
        except Student_Assistant_Model.DoesNotExist:
            messages.warning(request,u'操作错误')
            return HttpResponseRedirect(reverse('error_page'))
    def get_show_assistant(self,request,ass_id,todo):
        students=Student_Assistant_Model.objects.all().exclude(username=u'未选择')
        return render_to_response(self.show_with_edit_and_add_template,{'students':students},RequestContext(request))
    def post_edit_assistant(self,request,ass_id,todo):
        try:
            name=request.POST['name']
            phone=request.POST['phone']
            email=request.POST['email']
            student=Student_Assistant_Model(username=name,phone=phone,email=email)
            student.id=ass_id
            student.save()
            return HttpResponseRedirect(reverse('assistant_edit_and_add'))
        except KeyError:
            messages.warning(request,u'输入数据错误')
            return HttpResponseRedirect(reverse('error_page'))
    def post_add_assistant(self,request,ass_id,todo):
        try:
            name=request.POST['name']
            phone=request.POST['phone']
            email=request.POST['email']
            student=Student_Assistant_Model(username=name,phone=phone,email=email)
            student.save()
            return HttpResponseRedirect(reverse('assistant_edit_and_add'))
        except KeyError:
            messages.warning(request,u'输入数据错误')
            return HttpResponseRedirect(reverse('error_page'))            
    @is_login
    @can_change_student_assistant
    def get(self,request,ass_id='',todo=''):
        if todo=='show':
            return self.get_show_assistant(request, ass_id, todo)
        if todo=='edit':
            return self.get_edit_assistant(request,ass_id,todo)
        if todo=='delete':
            return self.get_delete_assistant(request, ass_id, todo)
        if todo=='add':
            return self.get_add_assistant(request, ass_id, todo)
        messages.warning(request,u'不支持该操作')
        return HttpResponseRedirect(reverse('error_page')) 
    @is_login
    @can_change_student_assistant
    def post(self,request,ass_id='',todo=''):
        if todo=='edit':
            return self.post_edit_assistant(request,ass_id,todo)
        if todo=='add':
            return self.post_add_assistant(request, ass_id, todo)
        messages.warning(request,u'不支持该操作')
        return HttpResponseRedirect(reverse('error_page')) 
class Student_Assistant_Arange_Edit(View):
    edit_templates='student_assistant_arange_edit.html'
    check_templates='student_assistant_arange_check.html'
    def get_check(self,request,todo=''):
        try:
            exp_aranges=[{'week_order':arange['week_order'],'week':arange['week'],'time_order':arange['time_order']}\
                         for arange in Exp_Arangement_Model.objects.filter(exp_name__need_assistant=True).order_by('week_order','week','time_order').values('week_order','week','time_order').distinct()]
            student_aranges=[{'week_order':arange['week_order'],'week':arange['week'],'time_order':arange['time_order']}\
                             for arange in Student_Assistant_Arange_Model.objects.order_by('week_order','week','time_order').values('week_order','week','time_order').distinct()]
            new_aranges=[]
            delete_aranges=[]
            for exp_arange in exp_aranges:
                if exp_arange in student_aranges:
                    student_aranges.remove(exp_arange)
                else:
                    new_aranges.append(exp_arange)
            delete_aranges=student_aranges
            if len(new_aranges)>0:
                new_aranges_in_week_order_id=list(set([arange['week_order'] for arange in new_aranges]))
                new_aranges_in_week_order_abbr=[Week_Order_Model.objects.get(pk=week_order_id).abbr for week_order_id in new_aranges_in_week_order_id]
                new_aranges_msg=u','.join(str(item) for item in new_aranges_in_week_order_abbr)
                msg=u'发现新课程位于%s周,请注意安排' %(new_aranges_msg)
                messages.info(request,msg)
                
            if len(delete_aranges)>0:
                delete_aranges_in_week_order_id=list(set([arange['week_order'] for arange in delete_aranges]))
                delete_aranges_in_week_order_abbr=[Week_Order_Model.objects.get(pk=week_order_id).abbr for week_order_id in delete_aranges_in_week_order_id]
                delete_aranges_msg=u','.join(str(item) for item in delete_aranges_in_week_order_abbr)
                msg=u'部分课程因为调整被删除,这些课程位于%s周' %(delete_aranges_msg)
                messages.info(request,msg)            
            #change the Student_Assistant_Arange_Model add
            for arange in new_aranges:
                student=Student_Assistant_Model.objects.get(username=u'未选择')
                week_order=Week_Order_Model.objects.get(pk=int(arange['week_order']))
                week=Week_Model.objects.get(pk=int(arange['week']))
                time_order=Time_Order_Model.objects.get(pk=int(arange['time_order']))
                student_arange=Student_Assistant_Arange_Model(week_order=week_order,week=week,time_order=time_order,student=student)
                student_arange.save()
            #change the Student_Assistant_Arange_Model delete
            for arange in delete_aranges:
                week_order=Week_Order_Model.objects.get(pk=int(arange['week_order']))
                week=Week_Model.objects.get(pk=int(arange['week']))
                time_order=Time_Order_Model.objects.get(pk=int(arange['time_order']))
                student_arange=Student_Assistant_Arange_Model.objects.filter(week_order=week_order,week=week,time_order=time_order)
                student_arange.delete()
            
            unarange_count=Student_Assistant_Arange_Model.objects.filter(student__username=u'未选择').count()
            if unarange_count>0:
                unarange_in_week_order=[int(item.week_order.abbr) for item in Student_Assistant_Arange_Model.objects.filter(student__username=u'未选择')]
                unarange_in_week_order_distinct=list(set(unarange_in_week_order))
                unarange_msg=u','.join(str(item) for item in unarange_in_week_order_distinct)
                msg=u'共有%s次值班未安排，分别位于%s周' %(unarange_count,unarange_msg)
                messages.info(request,msg)
            new_arange_list=[]
            delete_arange_list=[]
            #change dict to models object
            for arange in new_aranges:
                student=Student_Assistant_Model.objects.get(username=u'未选择')
                week_order=Week_Order_Model.objects.get(pk=int(arange['week_order']))
                week=Week_Model.objects.get(pk=int(arange['week']))
                time_order=Time_Order_Model.objects.get(pk=int(arange['time_order']))
                student_arange=Student_Assistant_Arange_Model(week_order=week_order,week=week,time_order=time_order,student=student)
                new_arange_list.append(student_arange)
            #change dict to models object
            for arange in delete_aranges:
                week_order=Week_Order_Model.objects.get(pk=int(arange['week_order']))
                week=Week_Model.objects.get(pk=int(arange['week']))
                time_order=Time_Order_Model.objects.get(pk=int(arange['time_order']))
                student_arange=Student_Assistant_Arange_Model(week_order=week_order,week=week,time_order=time_order)
                delete_arange_list.append(student_arange)
                
            return render_to_response(self.check_templates,{'new_aranges':new_arange_list,'delete_aranges':delete_arange_list},RequestContext(request))    
        except Student_Assistant_Model.DoesNotExist:
            messages.error(request,u'学生助理未设置或设置不当(请进行初始设置)')
            return HttpResponseRedirect(reverse('error_page'))
    def get_edit(self,request,week_order_abbr='1',todo=''):
        week_list=Week_Model.objects.all().exclude(name=u'未选择').order_by('abbr')
        time_order_list=Time_Order_Model.objects.all().exclude(name=u'未选择').order_by('abbr')
        assistant_arange_wo_w=[{'time_order':arange.time_order.abbr,'week':arange.week.abbr}\
                               for arange in Student_Assistant_Arange_Model.objects.filter(week_order__abbr=week_order_abbr).order_by('time_order','week')]
        assistant_arange_st=[{'student':arange.student.id}\
                               for arange in Student_Assistant_Arange_Model.objects.filter(week_order__abbr=week_order_abbr).order_by('time_order','week')]
        assistant_arange=[]
        for time_order in time_order_list:
            assistant_arange_in_to=[]
            left_label={'label':time_order.name}
            assistant_arange_in_to.append(left_label)
            for week in week_list:
                one_item={'time_order':time_order.abbr,'week':week.abbr}    
                if one_item in assistant_arange_wo_w:
                    index=assistant_arange_wo_w.index(one_item)
                    one_item['student']=assistant_arange_st[index]['student']
                    week_order=Week_Order_Model.objects.get(abbr=week_order_abbr)
                    week=Week_Model.objects.get(abbr=one_item['week'])
                    time_order=Time_Order_Model.objects.get(abbr=one_item['time_order'])
                    student=Student_Assistant_Model.objects.get(pk=one_item['student'])
                    student_ass=Student_Assistant_Arange_Model(week_order=week_order,week=week,time_order=time_order,student=student)
                    assistant_arange_in_to.append(student_ass)
                else:
                    student_ass={'null':u'空闲'}
                    assistant_arange_in_to.append(student_ass)
            assistant_arange.append(assistant_arange_in_to)
        week_order=Week_Order_Model.objects.get(abbr=week_order_abbr) 
        week_order_list=Week_Order_Model.objects.all().exclude(name='未选择').order_by('abbr')   
        student_assistants=Student_Assistant_Model.objects.all()
        response_dic={'week_order':week_order,\
                      'week_order_list':week_order_list,\
                      'week_list':week_list,\
                      'time_order_list':time_order_list,'assistant_arange':assistant_arange,\
                      'student_assistants':student_assistants}   
        return render_to_response(self.edit_templates,response_dic,RequestContext(request))
    def post_edit(self,request,week_order_abbr='1',todo=''):
        time_order_abbr_list=[item.abbr for item in Time_Order_Model.objects.all().exclude(name=u'未选择')]
        week_abbr_list=[item.abbr for item in Week_Model.objects.all().exclude(name=u'未选择')]
        for time_order_abbr in time_order_abbr_list:
            for week_abbr in week_abbr_list:
                pattern='%s-%s' %(time_order_abbr,week_abbr)
                if request.POST.has_key(pattern):
                    selected_student=request.POST[pattern]
                    assistant_arange=Student_Assistant_Arange_Model.objects.get(week_order__abbr=week_order_abbr,\
                                                                                week__abbr=week_abbr,\
                                                                                time_order__abbr=time_order_abbr)
                    assistant_arange.student=Student_Assistant_Model.objects.get(pk=selected_student)
                    assistant_arange.save()
        return HttpResponseRedirect(reverse('assistant_arange_edit',args=[week_order_abbr]))
    def get(self,request,week_order_abbr='',todo=''):
        if todo=='check':
            return self.get_check(request, todo)
        if todo=='edit':
            return self.get_edit(request,week_order_abbr, todo)
        else:
            messages.warning(request, u'不支持该操作')
            return HttpResponseRedirect(reverse('error_page'))
    def post(self,request,week_order_abbr='',todo=''):
        if todo=='edit':
            return self.post_edit(request, week_order_abbr, todo)
        else:
            messages.warning(request, u'不支持该操作')
            return HttpResponseRedirect(reverse('error_page'))
class Show_Assistant_Arange_In_Weekorder_Mode(View):
    template='show_assistant_arange_in_week_mode.html'
    def get(self,request,week_order_abbr=''):
        week_list=Week_Model.objects.all().exclude(name=u'未选择').order_by('abbr')
        time_order_list=Time_Order_Model.objects.all().exclude(name=u'未选择').order_by('abbr')
        assistant_arange_wo_w=[{'time_order':arange.time_order.abbr,'week':arange.week.abbr}\
                               for arange in Student_Assistant_Arange_Model.objects.filter(week_order__abbr=week_order_abbr).order_by('time_order','week')]
        assistant_arange_st=[{'student':arange.student.id}\
                               for arange in Student_Assistant_Arange_Model.objects.filter(week_order__abbr=week_order_abbr).order_by('time_order','week')]
        assistant_arange=[]
        for time_order in time_order_list:
            assistant_arange_in_to=[]
            left_label={'label':time_order.name}
            assistant_arange_in_to.append(left_label)
            for week in week_list:
                one_item={'time_order':time_order.abbr,'week':week.abbr}    
                if one_item in assistant_arange_wo_w:
                    index=assistant_arange_wo_w.index(one_item)
                    one_item['student']=assistant_arange_st[index]['student']
                    week_order=Week_Order_Model.objects.get(abbr=week_order_abbr)
                    week=Week_Model.objects.get(abbr=one_item['week'])
                    time_order=Time_Order_Model.objects.get(abbr=one_item['time_order'])
                    student=Student_Assistant_Model.objects.get(pk=one_item['student'])
                    student_ass=Student_Assistant_Arange_Model(week_order=week_order,week=week,time_order=time_order,student=student)
                    assistant_arange_in_to.append(student_ass)
                else:
                    student_ass={'null':u'空闲'}
                    assistant_arange_in_to.append(student_ass)
            assistant_arange.append(assistant_arange_in_to)
        week_order=Week_Order_Model.objects.get(abbr=week_order_abbr) 
        week_order_list=Week_Order_Model.objects.all().exclude(name='未选择').order_by('abbr')   
        #student_assistants=Student_Assistant_Model.objects.all()
        response_dic={'week_order':week_order,\
                      'week_order_list':week_order_list,\
                      'week_list':week_list,\
                      'time_order_list':time_order_list,'assistant_arange':assistant_arange}
                      #'student_assistants':student_assistants}           
        return render_to_response(self.template,response_dic,RequestContext(request))
    def post(self,request,week_order=''):
        messages.warning(request, u'不支持该操作')
        return HttpResponseRedirect(reverse('error_page'))