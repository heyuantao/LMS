#-*-coding:utf-8-*-
from django import template
from ASS.models import Student_Assistant_Arange_Model
register = template.Library()

@register.tag(name="assistant_at")
def assistant_at(parser,token):
    try:
        tag_name,week_order,week,time_order=token.split_contents()
    except ValueError:
        msg = '%r tag requires a single argument' % token.split_contents()[0]
        raise template.TemplateSyntaxError(msg)
    return Assistant_At_Node(week_order[1:-1],week[1:-1],time_order[1:-1],)
    #return System_Setting_Node("good")
class Assistant_At_Node(template.Node):
    def __init__(self,week_order,week,time_order):
        self.week_order = str(week_order)
        self.week = str(week)
        self.time_order = str(time_order)
    def render(self,context):
        try:
            #print self.week_order,self.week,self.time_order
            arange=Student_Assistant_Arange_Model.objects.get(week_order__name=self.week_order,\
                                                             week__name=self.week,\
                                                             time_order__name=self.time_order)
            return arange.student.username
        except Student_Assistant_Arange_Model.DoesNotExist:
            return u'未安排'
        #settings=System_Setting_Model.objects.get(key=self.format_string)
        #return settings.value
        #return "hello"