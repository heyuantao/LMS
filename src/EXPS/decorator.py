#-*-coding:utf-8-*-
from django.http.response import HttpResponseRedirect,HttpResponse
from EXPS.models import Exp_Model
def is_login(fun):
    def wrapped(self,request,*args,**kwargs):
        if request.user.is_authenticated():
            return fun(self,request,*args,**kwargs)
        else:
            return HttpResponseRedirect('/exps/course/login/')
    return wrapped

def is_superuser(fun):
    def wrapped(self,request,*args,**kwargs):
        if request.user.is_authenticated() and request.user.is_superuser:
            return fun(self,request,*args,**kwargs)
        else:
            return HttpResponseRedirect('/exps/course/login/')
    return wrapped
def can_change_aranges_or_exp(fun):
    def wrapped(self,request,exp_id='',*args,**kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/exps/course/login/')
        if ((Exp_Model.objects.get(pk=exp_id).user!=request.user)and(not request.user.is_superuser)):
            return HttpResponse(u'无操作权限')
        return fun(self,request,exp_id,*args,**kwargs)
    return wrapped

def can_change_student_assistant(fun):
    def wrapped(self,request,ass_id='',*args,**kwargs):
        if not request.user.is_superuser:
            return HttpResponseRedirect('/exps/course/login/')
        return fun(self,request,ass_id,*args,**kwargs)
    return wrapped
