#-*-coding:utf-8-*-
# here is user define exceptions
class System_Setting_Exception(Exception):
    def __init__(self,msg):
        self.msg=msg
    def __unicode__(self):
        return repr(self.msg)