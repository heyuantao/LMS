from EXPS.models import Exp_Model,Exp_Arangement_Model
from rest_framework import serializers

class Exp_Model_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Exp_Model
class Exp_Arangement_Model_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Exp_Arangement_Model