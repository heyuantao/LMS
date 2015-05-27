#-*-coding:utf-8-*-
from EXPS.models import Location_Model
from django.template import RequestContext
def exp_location_processor(request):
    location_list=[]
    for location in Location_Model.objects.all():
        if location.name!=u'未选择' and location.name!=u'外系实验室':
            location_list.append(location)
    return {'exp_location_list':location_list}