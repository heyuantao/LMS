#-*-coding:utf-8-*-
from EXPS.models import Exp_Model, Exp_Arangement_Model, Exp_Type_Model,\
    Week_Model, Week_Order_Model, Time_Order_Model, Location_Model,\
    System_Setting_Model
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
from EXPS.decorator import is_login,can_change_aranges_or_exp,is_superuser
from ASS.models import Student_Assistant_Arange_Model, Student_Assistant_Model
from EXPS.exceptions import System_Setting_Exception
from django.utils.datastructures import MultiValueDictKeyError
#from django.contrib.messages import constants as messages

# Create your views here.
class Arange_Info(View):
    templates='arange_info.html'
    def get(self,request,exp_id='none'):
        try:
            exp_aranges=Exp_Arangement_Model.objects.filter(exp_name_id=exp_id).order_by('week_order','week','time_order')
            exp=Exp_Model.objects.get(pk=exp_id)
            assistant_aranges=[]
            for arange in exp_aranges:
                try:
		    if exp.need_assistant==True:
			assistant_arange=Student_Assistant_Arange_Model.objects.get(week_order=arange.week_order,week=arange.week,time_order=arange.time_order)
		    else:
			student=Student_Assistant_Model.objects.get(username=u'未选择')
			assistant_arange=Student_Assistant_Arange_Model(week_order=arange.week_order,week=arange.week,time_order=arange.time_order,student=student)
		except Student_Assistant_Arange_Model.DoesNotExist:
                    student=Student_Assistant_Model.objects.get(username=u'未选择')
                    assistant_arange=Student_Assistant_Arange_Model(week_order=arange.week_order,week=arange.week,time_order=arange.time_order,student=student)
                assistant_aranges.append(assistant_arange)
            aranges=zip(exp_aranges,assistant_aranges)
            return render_to_response(self.templates,{'aranges':aranges,'exp':exp},RequestContext(request))
        except (Exp_Model.DoesNotExist,Exp_Arangement_Model.DoesNotExist):
            messages.warning(request,'exp_id not found !')
            return HttpResponseRedirect(reverse('error_page'))
    def post(self,request,exp_id='none'):
        return HttpResponseRedirect(reverse('error_page'))
class Exp_Info(View):
    my_exp_templates='my_exp_info.html'
    all_exp_templates='all_exp_info.html'
    def clear_old_session(self,request):
        if request.session.has_key('exp'):
            del request.session['exp']
        if request.session.has_key('aranges'):
            del request.session['aranges']
            
    def get(self,request,todo=''):
        self.clear_old_session(request)
        if todo!='':
            if todo=='all_exps':
                exps=Exp_Model.objects.all() 
                return render_to_response(self.all_exp_templates,{'exps':exps},RequestContext(request))
            if todo=='my_exps':
                if request.user.is_authenticated():
                    if request.user.is_superuser:    
                        exps=Exp_Model.objects.all()
                    else:         
                        exps=Exp_Model.objects.filter(user=request.user.id) 
                    return render_to_response(self.my_exp_templates,{'exps':exps},RequestContext(request))
                else:
                    return HttpResponseRedirect(reverse('login'))
        else:
            return HttpResponse("Error in Exp_info get()")
        
    def post(self,request,todo='none'):
        return HttpResponseRedirect(reverse('error_page'))

class Site_Logout(View):
    @is_login
    def get(self,request):
        auth.logout(request)
        return HttpResponseRedirect(reverse('site_main_page'))
    def post(self,request):
        pass
class Site_Login(View):
    templates='login.html'
    def get(self,request):
        return render_to_response(self.templates,{},RequestContext(request))
    def post(self,request):
        action=request.POST['action']
        if action==u'登录':
            username=request.POST['username']
            password=request.POST['password']
            user=auth.authenticate(username=username,password=password)
            if ((user is not None) and (user.is_active)):
                auth.login(request,user)
                if user.is_superuser:
                    return HttpResponseRedirect(reverse('user_main_page'))
                else:
                    return HttpResponseRedirect(reverse('user_main_page'))
            else:
                messages.info(request,u'登录失败')
                return render_to_response(self.templates,{},RequestContext(request))
        if action==u'取消':
            return HttpResponseRedirect(reverse('site_main_page'))

class Site_Change_Password(View):
    templates='change_password.html'
    @is_login
    def get(self,request):
        return render_to_response(self.templates,{},RequestContext(request))
    @is_login
    def post(self,request):
        action=request.POST['action']
        if action==u'修改':
            old_password=request.POST['old_password']
            new_password1=request.POST['new_password1']
            new_password2=request.POST['new_password2']
            user=auth.authenticate(username=request.user.username,password=old_password)
            if new_password1!=new_password2:
                messages.info(request,u"两次输入的密码不一致")
                return render_to_response(self.templates,{},RequestContext(request))
            if ((user is not None) and (user.is_active)):
                if new_password1==new_password2:
                    user.set_password(new_password1)
                    user.save()
                    #messages.info(request,u"密码修改成功")
                    return HttpResponseRedirect(reverse('user_main_page'))
            else:
                messages.info(request,u"原始密码错误")
                return render_to_response(self.templates,{},RequestContext(request))
        if action==u'取消':
            return HttpResponseRedirect(reverse('user_main_page'))
    
    
class Site_Register(View):
    templates='register.html'
    def get(self,request):
        return render_to_response(self.templates)
    def post(self,request):
        action=request.POST['action']
        if action==u'注册':
            username=request.POST['username']
            password1=request.POST['password1']
            password2=request.POST['password2']
            email=request.POST['email']
            if ( (username=='') or (len(User.objects.filter(username=username))>0) ):
            	messages.info(request,u'该用户名无效')
                return render_to_response(self.templates,{},RequestContext(request))
            elif password1!=password2:
            	messages.info(request, u'密码不一致')
                return render_to_response(self.templates,{},RequestContext(request))
            elif u'@' not in email:
                messages.info(request, u'邮箱不正确')
                return render_to_response(self.templates,{},RequestContext(request))
            else:
                user=User(username=username, email=email)
                user.set_password(password1)
                user.save()
                #auth.login(request, user)
                return HttpResponseRedirect(reverse('login'))
                #return HttpResponseRedirect(reverse('login'))
        if action==u'取消':
            return HttpResponseRedirect(reverse('site_main_page'))
        else:
            return render_to_response(self.templates,{},RequestContext(request))
            
class Site_Main_Page(View):
    templates='site_main_page.html'
    def get(self,request):
        exp_list=Exp_Model.objects.all()
        return render_to_response(self.templates,{'exp_list':exp_list},RequestContext(request))
    def post(self,request):
        exp_list=Exp_Model.objects.all()
        return render_to_response(self.templates,{'exp_list':exp_list},RequestContext(request))
    
class Exp_Edit(View):
    add_templates='exp_add.html'
    edit_templates='exp_edit.html'
    
    def get_add(self,request):
    	exp_type_list=[{'name':exp_type.name,'abbr':exp_type.abbr} for exp_type in Exp_Type_Model.objects.all()]
        if request.session.has_key('exp'):
            exp=pickle.loads(request.session['exp'])
            return render_to_response(self.add_templates,{'exp':exp,'exp_type_list':exp_type_list},RequestContext(request))
        else:
            return render_to_response(self.add_templates,{'exp_type_list':exp_type_list},RequestContext(request))
    @can_change_aranges_or_exp
    def get_edit(self,request,exp_id=''):
    	exp_type_list=[{'name':exp_type.name,'abbr':exp_type.abbr} for exp_type in Exp_Type_Model.objects.all()]
    	if request.session.has_key('exp'):
            exp=pickle.loads(request.session['exp'])
            if exp_id==exp.id:
                return render_to_response(self.edit_templates,{'exp':exp,'exp_type_list':exp_type_list},RequestContext(request))
        
        exp=Exp_Model.objects.filter(id=exp_id)[0]
        #print exp.need_assistant
        aranges=exp.exp_arangement_model_set.all()
        request.session['exp']=pickle.dumps(exp)
        request.session['aranges']=pickle.dumps(aranges)
        return render_to_response(self.edit_templates,{'exp':exp,'exp_type_list':exp_type_list},RequestContext(request))
    
    @can_change_aranges_or_exp
    def get_delete(self,request,exp_id=''):
    	exp=Exp_Model.objects.filter(pk=exp_id)
        exp.delete()
        return HttpResponseRedirect(reverse('user_main_page'))

    @is_login
    def get(self,request,exp_id='',todo=''):
        exp_type_list=[{'name':exp_type.name,'abbr':exp_type.abbr} for exp_type in Exp_Type_Model.objects.all()]
        if todo=='add':
        	return self.get_add(request)
        if todo=='edit':
        	return self.get_edit(request,exp_id)
        if todo=='delete':
            return self.get_delete(request,exp_id)
        else:
            return HttpResponse("Error in Exp_Edit.get()")
    
    @is_login
    def post(self,request,exp_id='',todo=''):
         #exp_type_list=[{'name':exp_type.name,'abbr':exp_type.abbr} for exp_type in Exp_Type_Model.objects.all()]
         action=request.POST['action']
         if todo=='add':
            if action==u'上一步':
                return HttpResponseRedirect(reverse('user_main_page'))
        
            user=request.user
            exp_type=Exp_Type_Model.objects.get(abbr=request.POST['exp_type'])
            need_assistant=True
            if request.POST.has_key('need_assistant'):
                if request.POST['need_assistant']=='on':
                    need_assistant=True
            else:
                need_assistant=False
            exp=Exp_Model(user=user,exp_name=request.POST['exp_name'],\
                          theory_class=request.POST['exp_theory_class'],\
                          student_grade=request.POST['exp_class_grade'],\
                          student_subject=request.POST['exp_class_subject'],\
                          student_num=request.POST['exp_student_num'],\
                          teachers=request.POST['exp_teacher'],\
                          exp_type=exp_type,need_assistant=need_assistant,\
			  exp_number_by_authority=request.POST['exp_number_by_authority'],\
			  exp_time_by_authority=request.POST['exp_time_by_authority'],\
			  exp_number_by_plan=request.POST['exp_number_by_plan'],\
			  exp_time_by_plan=request.POST['exp_time_by_plan'],\
                          other_info=request.POST['exp_other_info'])

         if todo=='edit':
            if action==u'上一步':
                return HttpResponseRedirect(reverse('user_main_page'))
            #user=User.objects.get(username=request.user.username)
            user=Exp_Model.objects.get(pk=exp_id).user
            exp_type=Exp_Type_Model.objects.get(abbr=request.POST['exp_type'])
            need_assistant=True
            if request.POST.has_key('need_assistant'):
                if request.POST['need_assistant']=='on':
                    need_assistant=True
            else:
                need_assistant=False
            exp=Exp_Model(user=user,exp_name=request.POST['exp_name'],\
                          theory_class=request.POST['exp_theory_class'],\
                          student_grade=request.POST['exp_class_grade'],\
                          student_subject=request.POST['exp_class_subject'],\
                          student_num=request.POST['exp_student_num'],\
                          teachers=request.POST['exp_teacher'],\
                          exp_type=exp_type,need_assistant=need_assistant,\
			  exp_number_by_authority=request.POST['exp_number_by_authority'],\
			  exp_time_by_authority=request.POST['exp_time_by_authority'],\
			  exp_number_by_plan=request.POST['exp_number_by_plan'],\
			  exp_time_by_plan=request.POST['exp_time_by_plan'],\
                          other_info=request.POST['exp_other_info'])
            exp.id=exp_id
         
         if action==u'下一步':
            request.session['exp']=pickle.dumps(exp)
            if exp_id!='':
                args=[exp_id]
                return HttpResponseRedirect(reverse('arange_edit',args=args))
            else:
                return HttpResponseRedirect(reverse('arange_add'))
        
class Arange_Edit(View):
    add_templates='arange_add.html'
    edit_templates='arange_edit.html'
    admin_add_templates='admin_arange_add.html'
    admin_edit_templates='admin_arange_edit.html'
    
    def admin_add_get(self,request,exp_id='',todo=''):
        week_list=[{'name':week.name,'abbr':week.abbr} for week in Week_Model.objects.all()]
        week_order_list=[{'name':week_order.name,'abbr':week_order.abbr} for week_order in Week_Order_Model.objects.all()]
        time_order_list=[{'name':time_order.name,'abbr':time_order.abbr} for time_order in Time_Order_Model.objects.all()]
        location_list=[{'name':location.name,'abbr':location.abbr} for location in Location_Model.objects.all()]
        if request.session.has_key('aranges'):
            aranges=pickle.loads(request.session['aranges'])
            return render_to_response(self.admin_add_templates,{'aranges':aranges,'location_list':location_list,'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))
        else:
            aranges=[]
            exp=pickle.loads(request.session['exp'])
            for i in range(1,8):
                arange=self.a_empty_arange(request)
                aranges.append(arange)
            return render_to_response(self.admin_add_templates,{'exp':exp,'aranges':aranges,'location_list':location_list,'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))
 
    def user_add_get(self,request,exp_id='',todo=''):
        week_list=[{'name':week.name,'abbr':week.abbr} for week in Week_Model.objects.all()]
        week_order_list=[{'name':week_order.name,'abbr':week_order.abbr} for week_order in Week_Order_Model.objects.all()]
        time_order_list=[{'name':time_order.name,'abbr':time_order.abbr} for time_order in Time_Order_Model.objects.all()]
        if request.session.has_key('aranges'):
            aranges=pickle.loads(request.session['aranges'])
            return render_to_response(self.add_templates,{'aranges':aranges,'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))
        else:
            aranges=[]
            exp=pickle.loads(request.session['exp'])
            for i in range(1,8):
                arange=self.a_empty_arange(request)
                aranges.append(arange)
            return render_to_response(self.add_templates,{'exp':exp,'aranges':aranges,'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))
 
    def admin_edit_get(self,request,exp_id='',todo=''):
        week_list=[{'name':week.name,'abbr':week.abbr} for week in Week_Model.objects.all()]
        week_order_list=[{'name':week_order.name,'abbr':week_order.abbr} for week_order in Week_Order_Model.objects.all()]
        time_order_list=[{'name':time_order.name,'abbr':time_order.abbr} for time_order in Time_Order_Model.objects.all()]
        location_list=[{'name':location.name,'abbr':location.abbr} for location in Location_Model.objects.all()]
        exp=pickle.loads(request.session['exp'])
        aranges=pickle.loads(request.session['aranges'])
        return render_to_response(self.admin_edit_templates,{'exp':exp,'aranges':aranges,'location_list':location_list,'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))

    def user_edit_get(self,request,exp_id='',todo=''):
        week_list=[{'name':week.name,'abbr':week.abbr} for week in Week_Model.objects.all()]
        week_order_list=[{'name':week_order.name,'abbr':week_order.abbr} for week_order in Week_Order_Model.objects.all()]
        time_order_list=[{'name':time_order.name,'abbr':time_order.abbr} for time_order in Time_Order_Model.objects.all()]
        exp=pickle.loads(request.session['exp'])
        aranges=pickle.loads(request.session['aranges'])
        return render_to_response(self.edit_templates,{'exp':exp,'aranges':aranges,'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))
    @is_login
    def get(self,request,exp_id='',todo=''):
        if not request.user.is_superuser:
            if todo=='add':
                return self.user_add_get(request, exp_id, todo)
            if todo=='edit':
                return self.user_edit_get(request, exp_id, todo)
            else:
                return HttpResponseRedirect(reverse('error_page'))
        if request.user.is_superuser:
            if todo=='add':
                return self.admin_add_get(request, exp_id, todo)
            if todo=='edit':
                return self.admin_edit_get(request, exp_id, todo)
            else:
                return HttpResponseRedirect(reverse('error_page'))
    
    def admin_edit_post(self,request,exp_id='',todo=''):
        week_list=[{'name':week.name,'abbr':week.abbr} for week in Week_Model.objects.all()]
        week_order_list=[{'name':week_order.name,'abbr':week_order.abbr} for week_order in Week_Order_Model.objects.all()]
        time_order_list=[{'name':time_order.name,'abbr':time_order.abbr} for time_order in Time_Order_Model.objects.all()]
        location_list=[{'name':location.name,'abbr':location.abbr} for location in Location_Model.objects.all()]
        action=request.POST['action']
        action=action.split(":")
        cmd=action[0]
        if cmd==u'删除':
            del_index=int(action[1])
            aranges=self.request_data_to_aranges(request)
            del aranges[del_index]
            exp=pickle.loads(request.session['exp'])
            return render_to_response(self.admin_edit_templates,{'exp':exp,'aranges':aranges,'location_list':location_list,'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))
        if cmd==u'添加':
            aranges=self.request_data_to_aranges(request)
            aranges.append(self.a_empty_arange(request))
            exp=pickle.loads(request.session['exp'])
            return render_to_response(self.admin_edit_templates,{'exp':exp,'aranges':aranges,'location_list':location_list,'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))
        if cmd==u'上一步':
            aranges=self.request_data_to_aranges(request)
            request.session['aranges']=pickle.dumps(aranges)
            args=[exp_id]
            return HttpResponseRedirect(reverse('exp_edit',args=args))
        if cmd==u'下一步':
            aranges=self.request_data_to_aranges(request)
            request.session['aranges']=pickle.dumps(aranges)
            args=[exp_id]
            return HttpResponseRedirect(reverse('exp_aranges_edit_finished',args=args))     
     
    def admin_add_post(self,request,exp_id='',todo=''):
        week_list=[{'name':week.name,'abbr':week.abbr} for week in Week_Model.objects.all()]
        week_order_list=[{'name':week_order.name,'abbr':week_order.abbr} for week_order in Week_Order_Model.objects.all()]
        time_order_list=[{'name':time_order.name,'abbr':time_order.abbr} for time_order in Time_Order_Model.objects.all()]    
        location_list=[{'name':location.name,'abbr':location.abbr} for location in Location_Model.objects.all()]
        action=request.POST['action']
        action=action.split(":")
        cmd=action[0]
        if cmd==u'删除':
            del_index=int(action[1])
            exp=pickle.loads(request.session['exp'])
            aranges=self.request_data_to_aranges(request)
            del aranges[del_index]
            return render_to_response(self.admin_add_templates,{'exp':exp,'aranges':aranges,'location_list':location_list,'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))
        if cmd==u'添加':
            aranges=self.request_data_to_aranges(request)
            aranges.append(self.a_empty_arange(request))
            exp=pickle.loads(request.session['exp'])
            return render_to_response(self.admin_add_templates,{'exp':exp,'aranges':aranges,'location_list':location_list,'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))
        if cmd==u'上一步':
            aranges=self.request_data_to_aranges(request)
            request.session['aranges']=pickle.dumps(aranges)
            return HttpResponseRedirect(reverse('exp_add'))
        if cmd==u'下一步':
            aranges=self.request_data_to_aranges(request)
            request.session['aranges']=pickle.dumps(aranges)
            return HttpResponseRedirect(reverse('exp_aranges_add_finished'))
    def user_add_post(self,request,exp_id='',todo=''):    
        week_list=[{'name':week.name,'abbr':week.abbr} for week in Week_Model.objects.all()]
        week_order_list=[{'name':week_order.name,'abbr':week_order.abbr} for week_order in Week_Order_Model.objects.all()]
        time_order_list=[{'name':time_order.name,'abbr':time_order.abbr} for time_order in Time_Order_Model.objects.all()]    
        action=request.POST['action']
        action=action.split(":")
        cmd=action[0]
        if cmd==u'删除':
            del_index=int(action[1])
            exp=pickle.loads(request.session['exp'])
            aranges=self.request_data_to_aranges(request)
            del aranges[del_index]
            return render_to_response(self.add_templates,{'exp':exp,'aranges':aranges,'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))

        if cmd==u'添加':
            aranges=self.request_data_to_aranges(request)
            aranges.append(self.a_empty_arange(request))
            exp=pickle.loads(request.session['exp'])
            return render_to_response(self.add_templates,{'exp':exp,'aranges':aranges,'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))
        if cmd==u'上一步':
            aranges=self.request_data_to_aranges(request)
            request.session['aranges']=pickle.dumps(aranges)
            return HttpResponseRedirect(reverse('exp_add'))
        if cmd==u'下一步':
            aranges=self.request_data_to_aranges(request)
            request.session['aranges']=pickle.dumps(aranges)
            return HttpResponseRedirect(reverse('exp_aranges_add_finished'))
    def user_edit_post(self,request,exp_id='',todo=''):   
        week_list=[{'name':week.name,'abbr':week.abbr} for week in Week_Model.objects.all()]
        week_order_list=[{'name':week_order.name,'abbr':week_order.abbr} for week_order in Week_Order_Model.objects.all()]
        time_order_list=[{'name':time_order.name,'abbr':time_order.abbr} for time_order in Time_Order_Model.objects.all()]
        action=request.POST['action']
        action=action.split(":")
        cmd=action[0]
        if cmd==u'删除':
            del_index=int(action[1])
            aranges=self.request_data_to_aranges(request)
            del aranges[del_index]
            exp=pickle.loads(request.session['exp'])
            return render_to_response(self.edit_templates,{'exp':exp,'aranges':aranges,'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))
        if cmd==u'添加':
            aranges=self.request_data_to_aranges(request)
            aranges.append(self.a_empty_arange(request))
            exp=pickle.loads(request.session['exp'])
            return render_to_response(self.edit_templates,{'exp':exp,'aranges':aranges,'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))
        if cmd==u'上一步':
            aranges=self.request_data_to_aranges(request)
            request.session['aranges']=pickle.dumps(aranges)
            args=[exp_id]
            return HttpResponseRedirect(reverse('exp_edit',args=args))
        if cmd==u'下一步':
            aranges=self.request_data_to_aranges(request)
            request.session['aranges']=pickle.dumps(aranges)
            args=[exp_id]
            return HttpResponseRedirect(reverse('exp_aranges_edit_finished',args=args))
    @is_login    
    def post(self,request,exp_id='',todo=''):
        if not request.user.is_superuser:
            if todo=='add':
                return self.user_add_post(request,exp_id,todo)            
            if todo=='edit':
                return self.user_edit_post(request,exp_id,todo)
        if request.user.is_superuser:
            if todo=='add':
                return self.admin_add_post(request,exp_id,todo)            
            if todo=='edit':
                return self.admin_edit_post(request,exp_id,todo) 
        else:
            return HttpResponseRedirect(reverse('error_page'))   
    def a_empty_arange(self,request):
        #exp=pickle.loads(request.session['exp'])
        week=Week_Model.objects.get(name=u'未选择')
        week_order=Week_Order_Model.objects.get(name=u'未选择')
        time_order=Time_Order_Model.objects.get(name=u'未选择')
        location=Location_Model.objects.get(name=u'未选择')
        #arange=Exp_Arangement_Model(exp_name=exp,week_order=week_order,week=week,time_order=time_order,item_name=u'未填写')
        arange=Exp_Arangement_Model(week_order=week_order,week=week,time_order=time_order,location=location,item_name=u'')
        return arange
    def request_data_to_aranges(self,request):
        wo_list=request.POST.getlist('wo')
        w_list=request.POST.getlist('w')
        to_list=request.POST.getlist('to')
        location_list=request.POST.getlist('location')
        item_name_list=request.POST.getlist('item_name')
        new_wo_list=[]
        new_w_list=[]
        new_to_list=[]
        new_location_list=[]
        new_item_name_list=[]
        for i in range(len(wo_list)):
            new_wo_list.append(wo_list[i])
            new_w_list.append(w_list[i])
            new_to_list.append(to_list[i])
            if (len(location_list)>0) and (location_list[i]!=u''):
                new_location_list.append(location_list[i])
            else:
                new_location_list.append(Location_Model.objects.get(name=u'未选择').abbr)
            new_item_name_list.append(item_name_list[i])
        aranges=[]
        #exp=pickle.loads(request.session['exp'])
        for i in range(len(new_wo_list)):
            wo=Week_Order_Model.objects.get(abbr=new_wo_list[i])
            w=Week_Model.objects.get(abbr=new_w_list[i])
            to=Time_Order_Model.objects.get(abbr=new_to_list[i])
            location=Location_Model.objects.get(abbr=new_location_list[i])
            item_name=new_item_name_list[i]
            arange=Exp_Arangement_Model(week_order=wo,week=w,time_order=to,location=location,item_name=item_name)
            #arange=Exp_Arangement_Model(exp_name=exp,week_order=wo,week=w,time_order=to,item_name=item_name)
            aranges.append(arange)
        return aranges

class Exp_Aranges_Finished(View):
    add_templates='exp_aranges_add_finish.html'
    edit_templates='exp_aranges_edit_finish.html'
    def exp_ananges_check(self,request,exp,aranges):
        return_status=True
        if exp.exp_name=='':
            messages.error(request,u'实验名称为空')
            return_status=False
        if exp.theory_class=='':
            messages.error(request,u'所属理论课字段为空')
            return_status=False
        if exp.student_grade=='':
            messages.error(request,u'学生年级未填写')
            return_status=False
        if exp.student_subject=='':
            messages.error(request,u'学生专业未填写')
            return_status=False
        if exp.student_num=='':
            messages.error(request,u'学生人数未填写')
            return_status=False
        if not exp.student_num.isdigit():
            messages.error(request,u'学生人数字段格式错误')
            return_status=False
        if exp.teachers=='':
            messages.error(request,u'教师信息未填写')
            return_status=False    
        if exp.exp_type.name==u'未选择':
            messages.error(request,u'课程类型未填写')
            return_status=False
        if len(aranges)==0:    
            messages.error(request,u'无课程安排')
            return_status=False
        if exp.exp_type.name==u'实验':
            for arange in aranges:
                if arange.item_name==u'':
                    messages.error(request, u'未填写实验名称')
                    return_status=False
                    break
        return return_status
    def post_edit_save(self,old_aranges,new_aranges,exp): #two param is list,and item is db object
	if len(old_aranges)==len(new_aranges):
	    for index,arange in enumerate(new_aranges):
		old_aranges[index].exp_name=exp
		old_aranges[index].week_order=arange.week_order
		old_aranges[index].week=arange.week
		old_aranges[index].time_order=arange.time_order
		old_aranges[index].item_name=arange.item_name
		old_aranges[index].location=arange.location
		old_aranges[index].save()
	if len(old_aranges)<len(new_aranges):
	    old_aranges_len=len(old_aranges)
	    for index in range(old_aranges_len): #update the old_aranges
		old_aranges[index].exp_name=exp
		old_aranges[index].week_order=new_aranges[index].week_order
		old_aranges[index].week=new_aranges[index].week
		old_aranges[index].time_order=new_aranges[index].time_order
		old_aranges[index].item_name=new_aranges[index].item_name
		old_aranges[index].location=new_aranges[index].location
		old_aranges[index].save()
	    #insert the new aranges
	    for index in range(old_aranges_len,len(new_aranges)):
		new_aranges[index].exp_name=exp
		new_aranges[index].save()
	if len(old_aranges)>len(new_aranges):
	    new_aranges_len=len(new_aranges)
	    for index in range(new_aranges_len):
		old_aranges[index].exp_name=exp
		old_aranges[index].week_order=new_aranges[index].week_order
		old_aranges[index].week=new_aranges[index].week
		old_aranges[index].time_order=new_aranges[index].time_order
		old_aranges[index].item_name=new_aranges[index].item_name
		old_aranges[index].location=new_aranges[index].location
		old_aranges[index].save()
	    for index in range(new_aranges_len,len(old_aranges)):
		old_aranges[index].delete()
    @is_login
    def get(self,request,exp_id='',todo=''):
        if todo=='add':
            exp=pickle.loads(request.session['exp'])
            aranges=pickle.loads(request.session['aranges'])
            exp,aranges=self.clear_emtpy_fields(request,exp,aranges)
            self.exp_ananges_check(request, exp, aranges)
            return render_to_response(self.add_templates,{'exp':exp,'aranges':aranges},RequestContext(request))
        if todo=='edit':
            exp=pickle.loads(request.session['exp'])
            aranges=pickle.loads(request.session['aranges'])
            exp,aranges=self.clear_emtpy_fields(request,exp,aranges)
            self.exp_ananges_check(request, exp, aranges)
            return render_to_response(self.edit_templates,{'exp':exp,'aranges':aranges},RequestContext(request))
    @is_login
    def post(self,request,exp_id='',todo=''):
        action=request.POST['action']
        if todo=='add':
            if action==u'上一步':
                return HttpResponseRedirect(reverse('arange_add'))
            if action==u'确定':
                exp=pickle.loads(request.session['exp'])
                aranges=pickle.loads(request.session['aranges'])
                exp=self.clear_exp_special_fields(request, exp)
                exp,aranges=self.clear_emtpy_fields(request,exp, aranges)
                exp.save()
                for arange in aranges:
                    arange.exp_name=exp
                    arange.save()
                del request.session['exp']
                del request.session['aranges']
                return HttpResponseRedirect(reverse('user_main_page'))
        if todo=='edit':
            if action==u'上一步':
                args=[exp_id]
                return HttpResponseRedirect(reverse('arange_edit',args=args))
            if action==u'确定':
                old_exp=Exp_Model.objects.get(pk=exp_id)
                old_aranges_queryset=old_exp.exp_arangement_model_set.all()
                old_aranges_list=[arange for arange in old_aranges_queryset] #change queryset to list

                new_exp=pickle.loads(request.session['exp'])
                new_aranges_list=pickle.loads(request.session['aranges'])
                new_exp=self.clear_exp_special_fields(request, new_exp)
                old_exp,new_aranges_list=self.clear_emtpy_fields(request,old_exp, new_aranges_list)
                #return HttpResponse("hello")
                #print exp.need_assistant
                new_exp.exp_id=old_exp.id
                new_exp.save()
                self.post_edit_save(old_aranges_list,new_aranges_list,new_exp)
                del request.session['exp']
                del request.session['aranges']
                return HttpResponseRedirect(reverse('user_main_page'))
    def clear_exp_special_fields(self,request,exp): #检查exp是否存在实验课特有信息为空的现象，如果存在则设置为0
        if exp.exp_number_by_authority==u'':
            exp.exp_number_by_authority=0
        if exp.exp_time_by_authority==u'':
            exp.exp_time_by_authority=0
        if exp.exp_number_by_plan==u'':
            exp.exp_number_by_plan=0
        if exp.exp_time_by_plan==u'':
            exp.exp_time_by_plan=0
        return exp
            
    def clear_emtpy_fields(self,request,exp,aranges):
        new_aranges=[]
        status_msgs=[]
        for arange in aranges:
            if (arange.week_order.name!=u'未选择') and (arange.week.name!=u'未选择') and (arange.time_order.name!=u'未选择'):
                new_aranges.append(arange)
        return (exp,new_aranges)
class Error_Page(View):
    templates='error_page.html'
    def get(self,request):
        return render_to_response(self.templates,{},RequestContext(request))
    def post(self,request):
        return HttpResponseRedirect(reverse('error_page'))
class Room_Exps_Info(View):
    templates='room_exps_info.html'
    def a_empty_arange(self,request):
        week=Week_Model.objects.get(name=u'未选择')
        week_order=Week_Order_Model.objects.get(name=u'未选择')
        time_order=Time_Order_Model.objects.get(name=u'未选择')
        location=Location_Model.objects.get(name=u'未选择')
        arange=Exp_Arangement_Model(week_order=week_order,week=week,time_order=time_order,location=location,item_name=u'')
        return arange
    def get_arange_by_id(self,dic):
        arange=Exp_Arangement_Model.objects.filter(week_order_id=dic['wo'],week_id=dic['w'],time_order_id=dic['to'],location=dic['location'])[0]
        return arange
    def get(self,request,room=''):
        location=Location_Model.objects.get(name=room)
        aranges_in_location=location.exp_arangement_model_set.all()
        aranges_list=[]
        for arange in aranges_in_location:
            t={'wo':arange.week_order.id,'w':arange.week.id,'to':arange.time_order.id,'location':arange.location.id}
            aranges_list.append(t)
        # peapare the info in aranges_list
        week_order_list=[wo.id for wo in Week_Order_Model.objects.all().exclude(name=u'未选择')]
        week_list=[w.id for w in Week_Model.objects.all().exclude(name=u'未选择')]
        time_order_list=[to.id for to in Time_Order_Model.objects.all().exclude(name=u'未选择')]
        # get the final_aranges_list
        final_aranges_list=[]
        top_side_label_list=[]
        top_side_cell={'label':u'星期'}
        top_side_label_list.append(top_side_cell)
        top_side_cell={'label':u'节次'}
        top_side_label_list.append(top_side_cell)
        for wo in week_order_list:
            top_side_cell={'label':Week_Order_Model.objects.get(pk=wo).name}
            top_side_label_list.append(top_side_cell)
        top_side_label_list=[top_side_label_list]
        final_aranges_list.append(top_side_label_list)
        empty_arange=self.a_empty_arange(request)
        for w in week_list:
            list_in_week=[]
            for to in time_order_list:
                list_in_time_order=[]
                left_side_label_order_1={'label':Week_Model.objects.get(pk=w).name}
                left_side_label_order_2={'label':Time_Order_Model.objects.get(pk=to).name}
                list_in_time_order.append(left_side_label_order_1)
                list_in_time_order.append(left_side_label_order_2)
                for wo in week_order_list:
                    item={'wo':wo,'w':w,'to':to,'location':location.id}
                    if item in aranges_list:
                        list_in_time_order.append(self.get_arange_by_id(item))
                    else:
                        list_in_time_order.append(empty_arange)
                list_in_week.append(list_in_time_order)
            final_aranges_list.append(list_in_week)
        return render_to_response(self.templates,{'room':room,'room_aranges':final_aranges_list},RequestContext(request))            
    def post(self,request):
        return HttpResponseRedirect(reverse('error_page'))

class Check_Aranges_Conflict(View):
    templates='check_aranges_conflict.html'
    def get(self,request):
        aranges=Exp_Arangement_Model.objects.all()
        aranges_wo_w_to_lo_list=[{'wo':arange.week_order.id,'w':arange.week.id,'to':arange.time_order.id,'location':arange.location.id} for arange in aranges]
        aranges_id_list=[{'id':arange.id} for arange in aranges]
        total_aranges_conflict=[]
        for i,arange in enumerate(aranges_wo_w_to_lo_list):
            conflict_to_this_one=[]
            conflict_index=[]
            if aranges_wo_w_to_lo_list.count(arange)>1:
                conflict_to_this_one.append(Exp_Arangement_Model.objects.get(pk=aranges_id_list[i]['id']))
                conflict_index=[j for j,item in enumerate(aranges_wo_w_to_lo_list) if item==arange]
                conflict_index.remove(i)
                for k in conflict_index:
                    conflict_to_this_one.append(Exp_Arangement_Model.objects.get(pk=aranges_id_list[k]['id']))
                total_aranges_conflict.append(conflict_to_this_one)
        total_aranges_conflict=total_aranges_conflict[0:len(total_aranges_conflict)/2]
        return render_to_response(self.templates,{'conflicts':total_aranges_conflict},RequestContext(request))            
                
    def post(self,request):
        return HttpResponseRedirect(reverse('error_page'))
    
class Table_Import_And_Export(View):    
    templates='files_manage/table_inport_and_export.html'
    exp_aranges_filename='exp_arange_input.xls'
    exp_aranges_download_file='exp_aranges_output.xls'
    assistant_aranges_filename='assistant_aranges_input.xls'
    assistant_aranges_download_file='assistant_aranges_ouput.xls'
    
    begin_line=0
    end_line=0
    current_exp_num=0
    def table_add_header(self,sheet):
        sheet_header_str=System_Setting_Model.objects.get(key='school_term').value
        sheet_header_str=sheet_header_str+u"实践教学安排表(仅包括实验和课程设计）"
        sheet_header_str_style=easyxf('align:vertical center,horizontal center')
        sheet_department_info=u'单位名称：计算机科学与应用系'
        sheet_table_properity=[u'序号',u'周次',u'星期',u'节次',u'年级',u'专业',u'人数',u'所属理论课',u'课程类型',u'实验或课程设计名称',u'实验教师',u'教室',u'其他信息',u'大纲指定的实验次数',u'大纲指定的实验学时',u'实际开设的实验次数',u'实际开设的实验学时']
        #print sheet_header_str
        sheet.write_merge(0,0,0,16,sheet_header_str,sheet_header_str_style)
        sheet.write_merge(1,1,0,16,sheet_department_info)
        for index,term in enumerate(sheet_table_properity):
            sheet.write(2,index,term)
    def db_to_exls(self):
        book=xlwt.Workbook(encoding='ascii')
        sheet1=book.add_sheet(u'实验室课表')
        self.table_add_header(sheet1)
        
        exps=Exp_Model.objects.all()
        current_line=3
        current_exp_id=1
        for exp in exps:
            aranges=exp.exp_arangement_model_set.all().order_by('week_order','week','time_order')
            id_style=easyxf('align:vertical center,horizontal center')
            if len(aranges)>0: 
                sheet1.write_merge(current_line,current_line+len(aranges)-1,0,0,str(current_exp_id),id_style) #如果存在len(arange)>0则这样处理
                for arange in aranges:
                    #sheet1.write(current_line,0,str(current_exp_id))
                    sheet1.write(current_line,1,arange.week_order.abbr)
                    sheet1.write(current_line,2,arange.week.abbr)
                    sheet1.write(current_line,3,arange.time_order.name)
                    sheet1.write(current_line,4,exp.student_grade)
                    sheet1.write(current_line,5,exp.student_subject)
                    sheet1.write(current_line,6,exp.student_num)
                    sheet1.write(current_line,7,exp.theory_class)
                    sheet1.write(current_line,8,exp.exp_type.name)
                    sheet1.write(current_line,9,arange.item_name)
                    sheet1.write(current_line,10,exp.teachers)
                    sheet1.write(current_line,11,arange.location.name)
                    sheet1.write(current_line,12,exp.other_info)
                    sheet1.write(current_line,13,exp.exp_number_by_authority)
                    sheet1.write(current_line,14,exp.exp_time_by_authority)
                    sheet1.write(current_line,15,exp.exp_number_by_plan)
                    sheet1.write(current_line,16,exp.exp_time_by_plan)
                    current_line=current_line+1
            else: #len(aranges)=0
                sheet1.write_merge(current_line,current_line,0,0,str(current_exp_id),id_style)
                sheet1.write(current_line,1,arange.week_order.abbr)
                sheet1.write(current_line,2,arange.week.abbr)
                sheet1.write(current_line,3,arange.time_order.name)
                sheet1.write(current_line,4,exp.student_grade)
                sheet1.write(current_line,5,exp.student_subject)
                sheet1.write(current_line,6,exp.student_num)
                sheet1.write(current_line,7,exp.theory_class)
                sheet1.write(current_line,8,exp.exp_type.name)
                sheet1.write(current_line,9,arange.item_name)
                sheet1.write(current_line,10,exp.teachers)
                sheet1.write(current_line,11,arange.location.name)
                sheet1.write(current_line,12,exp.other_info)
                sheet1.write(current_line,13,exp.exp_number_by_authority)
                sheet1.write(current_line,14,exp.exp_time_by_authority)
                sheet1.write(current_line,15,exp.exp_number_by_plan)
                sheet1.write(current_line,16,exp.exp_time_by_plan)
            #end the loop
            current_exp_id=current_exp_id+1 
        if os.path.exists(self.exp_aranges_download_file):
            os.remove(self.exp_aranges_download_file)
        book.save(self.exp_aranges_download_file)
        #return HttpResponseRedirect(reverse('error_page'))
    def str_format_change(self,str):
        if type(str)==float:
            str=int(str)
        if type(str)==int:
            str=int(str)
        str=unicode(str)
        str=str.replace(u'一', u'1').replace(u'二', u'2').replace(u'三', u'3').replace(u'四', u'4').replace(u'五', u'5').replace(u'六', u'6').replace(u'日', u'7').replace(u'七', u'7')
        str=str.replace(u'，',u',').replace(u'',u'').replace(u'-',u'-').replace(u'',u'').replace(u'、',u',')
        str=str.replace(u'节',u'')
        return_str=u''
        splited_str=str.split(',')
        for item in splited_str:
            if u'-' in item:
                item_list=item.split(u'-')
                for i in range(int(item_list[0]),int(item_list[1])+1):
                    return_str=return_str+unicode(i)+u','
            else:
                return_str=return_str+unicode(item)+u','
        return_str=return_str[:-1]
        return return_str
    def read_a_line(self,sheet):
        id_index_in_excel=0
        week_order_index_in_excel=1
        week_index_in_excel=2
        time_order_index_in_excel=3
        student_grade_index_in_excel=4
        student_subject_index_in_excel=5
        student_number_index_in_excel=6
        theory_class_index_in_excel=7
        exp_type_index_in_excel=8
        exp_item_name_index_in_excel=9
        teachers_index_in_excel=10
        location_index_in_excel=11
        other_info_index_in_excel=12
        exp_number_by_authority_index_in_excel=13
        exp_time_by_authority_index_in_excel=14
        exp_number_by_plan_index_in_excel=15
        exp_time_by_plan_index_in_excel=16
        
        if sheet.cell(self.current_line,id_index_in_excel).value!=u'':
            id=int(sheet.cell(self.current_line,id_index_in_excel).value)
            id=unicode(id)
            self.current_exp_num=id
        else:
            id=u''        
        week_order=sheet.cell(self.current_line,week_order_index_in_excel).value
        week_order=self.str_format_change(week_order)
        week=sheet.cell(self.current_line,week_index_in_excel).value
        week=self.str_format_change(week)
        time_order=sheet.cell(self.current_line,time_order_index_in_excel).value
        time_order=self.str_format_change(time_order)
        student_grade=sheet.cell(self.current_line,student_grade_index_in_excel).value
        student_grade=int(student_grade)
        student_grade=unicode(student_grade)
        student_subject=sheet.cell(self.current_line,student_subject_index_in_excel).value
        student_subject=unicode(student_subject)
        student_num=sheet.cell(self.current_line,student_number_index_in_excel).value
        student_num=int(student_num)
        student_num=unicode(student_num)
        theory_class=sheet.cell(self.current_line,theory_class_index_in_excel).value
        theory_class=unicode(theory_class)
        exp_type=sheet.cell(self.current_line,exp_type_index_in_excel).value
        exp_type=unicode(exp_type)
        exp_item_name=sheet.cell(self.current_line,exp_item_name_index_in_excel).value
        exp_item_name=unicode(exp_item_name)
        teachers=sheet.cell(self.current_line,teachers_index_in_excel).value
        teachers=unicode(teachers)
        location=sheet.cell(self.current_line,location_index_in_excel).value
        location=unicode(location)
        other_info=sheet.cell(self.current_line,other_info_index_in_excel).value
        other_info=unicode(other_info)   
        ######## 处理实验课特有信息
        exp_number_by_authority=sheet.cell(self.current_line,exp_number_by_authority_index_in_excel).value
        exp_number_by_authority=unicode(int(exp_number_by_authority))  
        exp_time_by_authority=sheet.cell(self.current_line,exp_time_by_authority_index_in_excel).value
        exp_time_by_authority=unicode(int(exp_time_by_authority))  
        exp_number_by_plan=sheet.cell(self.current_line,exp_number_by_plan_index_in_excel).value
        exp_number_by_plan=unicode(int(exp_number_by_plan))  
        exp_time_by_plan=sheet.cell(self.current_line,exp_time_by_plan_index_in_excel).value
        exp_time_by_plan=unicode(int(exp_time_by_plan))  
        #######     
        old_time_order=time_order
        time_order=''
        old_time_order=old_time_order.split(',')
        if u'1' in old_time_order:
            name=Time_Order_Model.objects.get(abbr=1).name
            time_order=time_order+name+','
        if u'3' in old_time_order:
            name=Time_Order_Model.objects.get(abbr=2).name
            time_order=time_order+name+','
        if u'5' in old_time_order:
            name=Time_Order_Model.objects.get(abbr=3).name
            time_order=time_order+name+','
        if u'7' in old_time_order:
            name=Time_Order_Model.objects.get(abbr=4).name
            time_order=time_order+name+','
        if u'9' in old_time_order:
            name=Time_Order_Model.objects.get(abbr=5).name
            time_order=time_order+name+','
        time_order=time_order[:-1]    
        line_dic={'id':id,'wo':week_order,'w':week,'to':time_order,\
                      'grade':student_grade,'subject':student_subject,'number':student_num,\
                      'theory':theory_class,'type':exp_type,'item_name':exp_item_name,\
                      'teachers':teachers,'location':location,'other_info':other_info,\
                      'exp_number_by_authority':exp_number_by_authority,'exp_time_by_authority':exp_time_by_authority,\
                      'exp_number_by_plan':exp_number_by_plan,'exp_time_by_plan':exp_time_by_plan}
        
        return line_dic
    def insert_line_into_db(self,request,line):
        if line['id']!=u'': #a new exp
            self.exp=Exp_Model(user=request.user,exp_name=line['theory'],theory_class=line['theory'],student_grade=line['grade'],\
                      student_subject=line['subject'],student_num=int(line['number']),\
                      teachers=line['teachers'],exp_type=Exp_Type_Model.objects.get(name=line['type']),\
                      other_info=line['other_info'],\
                      exp_number_by_authority=line['exp_number_by_authority'],exp_time_by_authority=line['exp_time_by_authority'],\
                      exp_number_by_plan=line['exp_number_by_plan'],exp_time_by_plan=line['exp_time_by_plan'])
            self.exp.save()
        wo_list=line['wo'].split(u',')
        w_list=line['w'].split(u',')
        to_list=line['to'].split(u',')
        for wo in wo_list:
            for w in w_list:
                for to in to_list:
                    #print wo,w,to
                    wo_item=Week_Order_Model.objects.get(abbr=wo)
                    w_item=Week_Model.objects.get(abbr=w)
                    to_item=Time_Order_Model.objects.get(name=to)
                    location=Location_Model.objects.get(name=line['location'])
                    arange=Exp_Arangement_Model(exp_name=self.exp,week_order=wo_item,week=w_item,\
                                                time_order=to_item,item_name=line['item_name'],\
                                                location=location)
                    #print arange.exp_name,arange.week_order.name,arange.week.name,arange.time_order.name
                    self.exp.exp_arangement_model_set.add(arange)
        
    def init_table_info(self,a_sheet):
        self.begin_line=3
        self.current_line=self.begin_line
        self.end_line=a_sheet.nrows-1
    def clear_db(self):
        Exp_Arangement_Model.objects.all().delete()
        Exp_Model.objects.all().delete()
    def read_file_into_db(self,request):
        a_excel_file=xlrd.open_workbook(self.exp_aranges_filename)
        a_sheet=a_excel_file.sheet_by_index(0)
        self.init_table_info(a_sheet)
        try:
            while self.current_line<=self.end_line:
                line=self.read_a_line(a_sheet)
                self.insert_line_into_db(request,line)
                self.current_line=self.current_line+1		
            messages.success(request,u'导入数据成功')
        except ValueError:
            self.clear_db()
            err_msg=u'数据表在第%s行有格式错误，请仔细检查'%(self.current_line)
            messages.error(request,err_msg)
        return render_to_response(self.templates,RequestContext(request))
    def exp_arange_table(self,request):
        action=request.POST['action']
        if action==u'上传':
	    try:
		file=request.FILES['file']
		with open(self.exp_aranges_filename,'wb+') as destination:
		    for chunk in file.chunks():
			destination.write(chunk)
		messages.success(request,u'上传文件成功')
	    except (MultiValueDictKeyError ):
		messages.error(request,u'文件上传失败')
            return render_to_response(self.templates,{},RequestContext(request))
        if action==u'下载':
            self.db_to_exls()
            f= open(self.exp_aranges_download_file,"rb")
            data = f.read()
            f.close()
            response=HttpResponse(data,content_type="application/ms-excel")
            response['Content-Disposition'] = 'attachment; filename="output.xls"'
            return response
        if action==u'清除':
            self.clear_db()
            messages.info(request,u'清除数据成功')
            return render_to_response(self.templates,RequestContext(request))
        if action==u'导入':
            if os.path.exists(self.exp_aranges_filename):
                self.clear_db() #clear the old exp_arange_table
                return self.read_file_into_db(request)
                messages.success(request,u'导入数据成功')
            else:
                messages.success(request,u'数据文件不存在，请上传后再导入！')
            return render_to_response(self.templates,RequestContext(request))
    def assistant_arange_table_upload(self,request):
	try:
	    file=request.FILES['file']
	    with open(self.assistant_aranges_filename,'wb+') as destination:
		for chunk in file.chunks():
		    destination.write(chunk)
	    messages.success(request,u'上传文件成功')
	except (NameError,MultiValueDictKeyError): # because no file update
	    messages.error(request,u'文件上传失败')
        return render_to_response(self.templates,{},RequestContext(request))
    def assistant_arange_table_load(self,request):
	try:
	    Student_Assistant_Arange_Model.objects.all().delete()
	    a_excel_file=xlrd.open_workbook(self.assistant_aranges_filename)
	    a_sheet=a_excel_file.sheet_by_index(0)
    
	    nrow=a_sheet.nrows-1
	    current_row=2
	    #read the file content into database table
	    while current_row<=nrow:
		id=a_sheet.cell(current_row,0).value
		week_order_value=a_sheet.cell(current_row,1).value
		week_value=a_sheet.cell(current_row,2).value
		time_order_value=a_sheet.cell(current_row,3).value
		student_value=a_sheet.cell(current_row,4).value
		#print id,week_order,week,time_order,student
		week_order=Week_Order_Model.objects.get(name=week_order_value)
		week=Week_Model.objects.get(name=week_value)
		time_order=Time_Order_Model.objects.get(name=time_order_value)
		student=Student_Assistant_Model.objects.get(username=student_value)
		arange=Student_Assistant_Arange_Model(week_order=week_order,\
						      week=week,\
						      time_order=time_order,\
						      student=student)
		arange.save()
		current_row=current_row+1
	    #end
	    messages.info(request,u'导入学生值班数据成功')
	except IOError:
	    messages.error(request,u'文件不存在或打开失败')	    
        return render_to_response(self.templates,{},RequestContext(request))
    def assistant_arange_table_download(self,request):
        book2=xlwt.Workbook(encoding='ascii')
        sheet2=book2.add_sheet(u'值班安排表')
        table_head=u'值班安排表'
        title_style=easyxf('align:vertical center,horizontal center')
        sheet2.write_merge(0,0,0,4,table_head,title_style)
        sheet2.write(1,0,u'序号')
        sheet2.write(1,1,u'周次')
        sheet2.write(1,2,u'周')
        sheet2.write(1,3,u'节次')
        sheet2.write(1,4,u'值班助理')
        current_line=2
        for arange in Student_Assistant_Arange_Model.objects.all():#.order_by('week_order','week','time_order'):
            sheet2.write(current_line,0,current_line-1)
            sheet2.write(current_line,1,arange.week_order.name)
            sheet2.write(current_line,2,arange.week.name)
            sheet2.write(current_line,3,arange.time_order.name)
            sheet2.write(current_line,4,arange.student.username)
            current_line=current_line+1
        #delete the per file
        if os.path.exists(self.assistant_aranges_download_file):
            os.remove(self.assistant_aranges_download_file)
        book2.save(self.assistant_aranges_download_file)
        ##begin download
        f= open(self.assistant_aranges_download_file,"rb")
        data = f.read()
        f.close()
        response=HttpResponse(data,content_type="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename="output.xls"'
        return response
    def assistant_arange_table_clear(self,request):
	Student_Assistant_Arange_Model.objects.all().delete()
	messages.info(request,u'学生助理信息表已清空')
        return render_to_response(self.templates,{},RequestContext(request))
    def assistant_aranges_table(self,request):
        action=request.POST['action']
        if action==u'上传':
            return self.assistant_arange_table_upload(request)
        if action==u'下载':
            return self.assistant_arange_table_download(request)
        if action==u'导入':
            return self.assistant_arange_table_load(request)
        if action==u'清除':
            return self.assistant_arange_table_clear(request)
        pass
    @is_login
    @is_superuser
    def get(self,request):
        return render_to_response(self.templates,RequestContext(request))
    @is_login
    @is_superuser
    def post(self,request):
        if request.POST['id']==u'exp_aranges_table':
            return self.exp_arange_table(request)
        if request.POST['id']==u'assistant_aranges_table':
            return self.assistant_aranges_table(request)
        else:
            messages.warning(request,u'不支持该操作')
            return HttpResponseRedirect(reverse('error_page'))
class System_Setting(View):
    error_page='system/error_page.html'
    templates='system_setting.html'
    
    @classmethod
    def str_to_date(cls,str): #this function my raise System_Setting_Exception with msg. if field is empty
	if len(str)==0:
	    raise System_Setting_Exception('error in Recent_Exps.str_to_data,because of len(str)==0')
	else:
	    split_str=str.split('-')
	    return date(int(split_str[0]),int(split_str[1]),int(split_str[2]))

    @classmethod
    def current_week_order_abbr(cls):
	current_week_order_abbr,current_week_abbr=cls.current_week_order_and_week_abbr()
	return current_week_order_abbr
    @classmethod
    def next_week_order_abbr(cls):
	return cls.current_week_order_abbr()+1
    @classmethod
    def current_week_order_and_week_abbr(cls): #this function may raise System_Setting_Exception
	try:
	    now=timezone.now()
	    now_date=date(now.year,now.month,now.day)
	    init_date=cls.str_to_date(System_Setting_Model.objects.get(key='init_date').value)
	    date_delta=now_date-init_date
	    current_week_order_abbr=date_delta.days/7+1
	    current_week_abbr=date_delta.days%7+1
	    return current_week_order_abbr,current_week_abbr
	except System_Setting_Model.DoesNotExist:
	    raise System_Setting_Exception('error in System_Setting.current_week_order_and_week_abbr() ')
    @classmethod 
    def tomorrow_week_order_and_week_abbr(cls): 
	current_week_order_abbr,current_week_abbr=cls.current_week_order_and_week_abbr()
	tomorrow_week_abbr=(current_week_abbr-1+1)%7+1
	if tomorrow_week_abbr==1: #如果为第一周，那么将周次加一
	    tomorrow_week_order_abbr=current_week_order_abbr+1
	else:
	    tomorrow_week_order_abbr=current_week_order_abbr
	#print current_week_order_abbr,current_week_abbr
	#print tomorrow_week_order_abbr,tomorrow_week_abbr
	return tomorrow_week_order_abbr,tomorrow_week_abbr
    
    def post_save(self,request):
        init_date=request.POST['init_date']
        init_date=init_date.split('-')
        if len(init_date)!=3:
            messages.info(request,u'日期格式错误')
            choice_date=date(2000,1,1)
            return render_to_response(self.templates,{'choice_date':choice_date},RequestContext(request))
        else:
            system_setting_item,created=System_Setting_Model.objects.get_or_create(key='init_date')
            system_setting_item.value=request.POST['init_date']
            system_setting_item.save()
            system_setting_item,created=System_Setting_Model.objects.get_or_create(key='school_term')
            system_setting_item.value=request.POST['school_term']
            system_setting_item.save()
            #choice_date=date(int(sys_init_date[0]),int(sys_init_date[1]),int(sys_init_date[2]))
            return render_to_response(self.templates,{},RequestContext(request))
    def post_init_table(self,request):
        room_list=request.POST['room_list']
        system_setting_item,created=System_Setting_Model.objects.get_or_create(key='room_list')
        room_list=room_list+u';外系实验室'
        system_setting_item.value=room_list

        system_setting_item.save()
                
        week_order_name_list=[u'第一周',u'第二周',u'第三周',u'第四周',u'第五周',u'第六周',u'第七周',u'第八周',u'第九周',u'第十周',\
                        u'第十一周',u'第十二周',u'第十三周',u'第十四周',u'第十五周',u'第十六周',u'第十七周',u'第十八周',u'第十九周']
        week_name_list=[u'周一',u'周二',u'周三',u'周四',u'周五',u'周六',u'周日']
        time_order_name_list=[u'1-2节',u'3-4节',u'5-6节',u'7-8节',u'9-10节']
        exp_type_name_list=[u'实验',u'课程设计',u'上机',u'实训']
        student_assistant_name_list=[]
        room_list=room_list.split(';')
        
        week_order_name_list.insert(0,u'未选择')
        week_name_list.insert(0, u'未选择')
        time_order_name_list.insert(0, u'未选择')
        room_list.insert(0, u'未选择')
        exp_type_name_list.insert(0, u'未选择')
        student_assistant_name_list.insert(0, u'未选择')
        
        if (Week_Order_Model.objects.all().count()>0)or(Week_Model.objects.all().count()>0)or(Time_Order_Model.objects.all().count()>0)or(Location_Model.objects.all().count()):
          messages.warning(request,u'系统已经初始化')
          return HttpResponseRedirect(reverse('error_page'))
        ##begin install the table
        for index,item in enumerate(week_order_name_list):
            Week_Order_Model.objects.create(abbr=index,name=item)
        for index,item in enumerate(week_name_list):
            Week_Model.objects.create(abbr=index,name=item)
        for index,item in enumerate(time_order_name_list):
            Time_Order_Model.objects.create(abbr=index,name=item)
        for index,item in enumerate(room_list):
            Location_Model.objects.create(abbr=index,name=item)
        for index,item in enumerate(exp_type_name_list):
            Exp_Type_Model.objects.create(abbr=index,name=item)  
        for index,item in enumerate(student_assistant_name_list):
            Student_Assistant_Model.objects.create(username=item)
        return render_to_response(self.templates,{},RequestContext(request))

    @is_superuser
    def get(self,request):
        system_setting_item1,created=System_Setting_Model.objects.get_or_create(key='init_date')
        system_setting_item2,created=System_Setting_Model.objects.get_or_create(key='school_term')
        return render_to_response(self.templates,{},RequestContext(request))
    @is_superuser
    def post(self,request):
        action=request.POST['action']
        if action==u'保存':
            return self.post_save(request)
        if action==u'初始化':
            return self.post_init_table(request)
        else:
            return HttpResponseRedirect(reverse('error_page'))
        
class Recent_Exps(View):
    templates='exp_info/recent_exps.html'
    def get(self,request):
        try:
            #current_week_order_abbr=date_delta.days/7+1
            #current_week_abbr=date_delta.days%7+1
	    current_week_order_abbr,current_week_abbr=System_Setting.current_week_order_and_week_abbr()
	    tomorrow_week_order_abbr,tomorrow_week_abbr=System_Setting.tomorrow_week_order_and_week_abbr()
	    current_aranges=Exp_Arangement_Model.objects.filter(week_order__abbr=current_week_order_abbr,week__abbr=current_week_abbr).exclude(location__name=u'外系实验室').order_by('time_order')
	    tomorrow_aranges=Exp_Arangement_Model.objects.filter(week_order__abbr=tomorrow_week_order_abbr,week__abbr=tomorrow_week_abbr).exclude(location__name=u'外系实验室').order_by('time_order')            
	    current_aranges_disp=[]
	    tomorrow_aranges_disp=[]
            
	    assistant_arange_list=[]
	    for arange in current_aranges: #将学生信息也加入
		try:
		    if arange.exp_name.need_assistant==True:
			assistant_arange=Student_Assistant_Arange_Model.objects.get(week_order=arange.week_order,week=arange.week,time_order=arange.time_order)
		    else:
			student=Student_Assistant_Model.objects.get(username=u'未选择')
			assistant_arange=Student_Assistant_Arange_Model(week_order=arange.week_order,week=arange.week,time_order=arange.time_order,student=student)
		except Student_Assistant_Arange_Model.DoesNotExist:
		    student=Student_Assistant_Model.objects.get(username=u'未选择')
		    assistant_arange=Student_Assistant_Arange_Model(week_order=arange.week_order,week=arange.week,time_order=arange.time_order,student=student)
		assistant_arange_list.append(assistant_arange)
	    current_aranges_disp=zip(current_aranges,assistant_arange_list)
	    
	    assistant_arange_list=[]
	    for arange in tomorrow_aranges: #将学生信息也加入
		try:
		    if arange.exp_name.need_assistant==True:
			assistant_arange=Student_Assistant_Arange_Model.objects.get(week_order=arange.week_order,week=arange.week,time_order=arange.time_order)
		    else:
			student=Student_Assistant_Model.objects.get(username=u'未选择')
			assistant_arange=Student_Assistant_Arange_Model(week_order=arange.week_order,week=arange.week,time_order=arange.time_order,student=student)		    
		except Student_Assistant_Arange_Model.DoesNotExist:
		    student=Student_Assistant_Model.objects.get(username=u'未选择')
		    assistant_arange=Student_Assistant_Arange_Model(week_order=arange.week_order,week=arange.week,time_order=arange.time_order,student=student)
		assistant_arange_list.append(assistant_arange)
	    tomorrow_aranges_disp=zip(tomorrow_aranges,assistant_arange_list)
		
	    return render_to_response(self.templates,{'current_aranges_disp':current_aranges_disp,'tomorrow_aranges_disp':tomorrow_aranges_disp},RequestContext(request))
	    #except (System_Setting_Model.DoesNotExist,System_Setting_Exception):
	except System_Setting_Exception:
            messages.error(request,u'系统未进行初始设置或设置错误')
            return render_to_response(System_Setting.error_page,{},RequestContext(request))
    def post(self,request):
        return HttpResponseRedirect(reverse('error_page'))
    
class Search_Exps(View):
    templates='exp_info/search_exps.html'
    def get(self,request):
        week_order_list=[{'name':week_order.name,'abbr':week_order.abbr} for week_order in Week_Order_Model.objects.all()]
        week_list=[{'name':week.name,'abbr':week.abbr} for week in Week_Model.objects.all()]
        time_order_list=[{'name':time_order.name,'abbr':time_order.abbr} for time_order in Time_Order_Model.objects.all()]
        
        return render_to_response(self.templates,{'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))
    def post(self,request):
        #messages.info(request, u'不支持POST请求')
        action=request.POST['action']
        if action==u'查找':
            teachers=request.POST['teachers']
            student_subject=request.POST['student_subject']
            week_order=Week_Order_Model.objects.get(abbr=request.POST['week_order'])
            week=Week_Model.objects.get(abbr=request.POST['week'])
            time_order=Time_Order_Model.objects.get(abbr=request.POST['time_order'])
            query_set=Exp_Arangement_Model.objects.all()
            if student_subject!=u'':
                query_set=query_set.filter(exp_name__student_subject__contains=student_subject)
            if teachers!=u'':
                query_set=query_set.filter(exp_name__teachers__contains=teachers)
            if week_order.name!=u'未选择':
               query_set=query_set.filter(week_order=week_order)
            if week.name!=u'未选择':
                query_set=query_set.filter(week=week)
            if time_order.name!=u'未选择':
                query_set=query_set.filter(time_order=time_order)
                
            exp_aranges=query_set.order_by('week_order','week','time_order').exclude(location__name=u'外系实验室')
        assistant_aranges=[]
        for arange in exp_aranges:
            try:
		if arange.exp_name.need_assistant==True:
		    assistant_arange=Student_Assistant_Arange_Model.objects.get(week_order=arange.week_order,week=arange.week,time_order=arange.time_order)
                else:
		    student=Student_Assistant_Model.objects.get(username=u'未选择')
		    assistant_arange=Student_Assistant_Arange_Model(week_order=arange.week_order,week=arange.week,time_order=arange.time_order,student=student)
		#assistant_aranges.append(assistant_arange)
            except Student_Assistant_Arange_Model.DoesNotExist:
                student=Student_Assistant_Model.objects.get(username=u'未选择')
                assistant_arange=Student_Assistant_Arange_Model(week_order=arange.week_order,week=arange.week,time_order=arange.time_order,student=student)
                #assistant_aranges.append(assistant_arange)
	    assistant_aranges.append(assistant_arange)
        disp_aranges=zip(exp_aranges,assistant_aranges)
        week_order_list=[{'name':week_order.name,'abbr':week_order.abbr} for week_order in Week_Order_Model.objects.all()]
        week_list=[{'name':week.name,'abbr':week.abbr} for week in Week_Model.objects.all()]
        time_order_list=[{'name':time_order.name,'abbr':time_order.abbr} for time_order in Time_Order_Model.objects.all()]
        
        return render_to_response(self.templates,{'disp_aranges':disp_aranges,'week_order_list':week_order_list,'week_list':week_list,'time_order_list':time_order_list},RequestContext(request))