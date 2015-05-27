from django import template
from EXPS.models import System_Setting_Model
register = template.Library()

@register.tag(name="system_setting")
def system_setting(parser,token):
    try:
        tag_name,format_string=token.split_contents()
    except ValueError:
        msg = '%r tag requires a single argument' % token.split_contents()[0]
        raise template.TemplateSyntaxError(msg)
    return System_Setting_Node(format_string[1:-1])
    #return System_Setting_Node("good")
class System_Setting_Node(template.Node):
    def __init__(self,string):
        self.format_string = str(string)
    def render(self,context):
        try:
            settings=System_Setting_Model.objects.get(key=self.format_string)
            return settings.value
        except System_Setting_Model.DoesNotExist:
            return u''
        #return "hello"