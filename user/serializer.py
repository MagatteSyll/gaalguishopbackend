from rest_framework import serializers
from .models import*
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer




class UserSerializer(serializers.ModelSerializer):
	phone = PhoneNumberField()
	prenom= serializers.CharField()
	nom= serializers.CharField()
	password = serializers.CharField()
	class Meta:
		model=User
		fields="__all__"
		extra_kwargs = {'password': {'write_only': True}}

	def create(self, validated_data):
		user = super(UserSerializer, self).create(validated_data)
		user.set_password(validated_data['password'])
		user.save()
		return user



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
    	if user.active==True and user.conform_phone==True:
    		token = super().get_token(user)
    		token['name'] = user.group
    		return token



class EmployeSerializer():
	user=serializers.SerializerMethodField()
	class Meta:
		model=Employe
		fields='__all__'

	def get_user(self,obj):
		return UserSerializer(obj.user).data



		