from django.contrib import admin
from EXPS.models import Week_Order_Model, Week_Model, Time_Order_Model,\
    Exp_Model, Exp_Arangement_Model, Exp_Type_Model,Location_Model

# Register your models here.
admin.site.register(Week_Model)
admin.site.register(Week_Order_Model)
admin.site.register(Time_Order_Model)
admin.site.register(Exp_Model)
admin.site.register(Exp_Arangement_Model)
admin.site.register(Exp_Type_Model)
admin.site.register(Location_Model)
