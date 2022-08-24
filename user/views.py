from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import*
from rest_framework.response import Response
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from produit.models import Boutique,Cart,Follower
from rest_framework import  permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from random import randint
from produit.serializer import NotificationSerializer,FollowerSerializer
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
#import vonage
import json
from rest_framework.pagination import PageNumberPagination
from firebase_admin.messaging import Message
from fcm_django.models import FCMDevice
from django.http import JsonResponse
import pyrebase
import os



 




def notif(user,data):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(user.group, {
    'type': 'notify',
    'value': data
    }) 
#client = vonage.Client(key="ba6aaf96", secret="kF38qLBVLFdlXFfG")
#sms = vonage.Sms(client)
def index(request):
	devices = FCMDevice.objects.filter(user__phone='+221772058140')
	for device in devices:
		device.send_message(Message(data={"titre": "Le titre","body":"le body"}))
		
	return JsonResponse({'status':'OK'})

class MyPaginationClass(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
 
def SMSVerif(numero,code):
	print('hey')
	'''responseData = sms.send_message(
		{
        "from": "GaalguiShop",
        "to": numero,
        "text": "Le code de confirmation de votre numero est "+" "+ str(code)
        }
        )
	if responseData["messages"][0]["status"] == "0":
		print('message envoye')
	else:
		print(f"Message failed with error: {responseData['messages'][0]['error-text']}")'''
			


class MyTokenObtainPairView(TokenObtainPairView):
	serializer_class=MyTokenObtainPairSerializer

class MyTokenRefreshPairView(TokenRefreshView):
	serializer_class=MyTokenObtainPairSerializer


class RegistrationView(APIView):
	permission_classes = [permissions.AllowAny]
	def post(self, request):
		data=request.data
		serializer=UserSerializer(data=data)
		if serializer.is_valid():
			user=serializer.save(active=False,conform_phone=False)
			code=randint(10000,99999)
			phoneconfir=CodeConfirmationPhone.objects.create(phone=user.phone,code=code,active=True)
			user.codeid=phoneconfir.id
			user.save()
			#SMSVerif(phone,code)
			return Response({'user_id':user.id,'code_id':phoneconfir.id,'prenom':user.prenom,'nom':user.nom})


class GetuserRegistration(APIView):
	permission_classes = [permissions.AllowAny]
	def post(self,request):
		id=request.data.get('id')
		user=User.objects.get(id=id,active=False,conform_phone=False,)
		serializer=UserSerializer(user)
		return Response(serializer.data)


class SuspensionUserRegistration(ModelViewSet):
	permission_classes = [permissions.AllowAny]
	queryset = User.objects.filter(active=False,conform_phone=False)
	serializer_class=UserSerializer
	@action(methods=["put"], detail=False, url_path='deleteuser/(?P<pk>\d+)')
	def supuser(self,request,*args,**kwargs):
		id=self.kwargs['pk']
		user=User.objects.get(id=id,active=False,conform_phone=False)
		user.delete()
		return Response({'message':'inscription suspendue'})




class PhoneConfirmationRegistration(APIView):
	permission_classes = [permissions.AllowAny]
	def post(self,request):
		id=request.data.get('id')
		code_id=request.data.get('code_id')
		code=int(request.data.get('code')) 
		confirm=CodeConfirmationPhone.objects.get(id=code_id)
		if confirm.code==code:
			user=User.objects.get(id=id)
			user.conform_phone=True
			user.active=True
			user.save()
			confirm.active=False
			confirm.save()
			Boutique.objects.create(user=user,note_vendeur=0,active=True)
			Cart.objects.create(proprietaire=user)
			Follower.objects.create(user=user)
			serializer=UserSerializer(user)
			return Response(serializer.data)



class GetUserChannel(APIView):
	permission_classes = [permissions.AllowAny]
	def get(self,request):  
		if request.user.is_authenticated:
			channel=request.user.channel
			return Response({'channel':channel})

class GetNotifications(generics.ListAPIView):
	permission_classes = [permissions.AllowAny]
	pagination_class =MyPaginationClass
	#queryset=Produit.objects.all()
	serializer_class=NotificationSerializer

	def get_queryset(self, *args, **kwargs):
		notifcationall=Notification.objects.filter(user=self.request.user,active=True).order_by('-id')
		return notifcationall
		
class GetBadgeNotif(APIView):
	def get(self,request):
		notifynolu=Notification.objects.filter(user=request.user,lu=False).count()
		return Response({'badge':notifynolu})
		

		
class Authent(APIView):
	permission_classes = [permissions.AllowAny]
	def get(self,request):
		if request.user.is_authenticated:
			return Response(True)
		else:
			return Response(False)

class GetNewUser(APIView):
	permission_classes = [permissions.AllowAny]
	def post(self,request):
		id=request.data.get('id')
		user=User.objects.get(id=id)
		serializer=UserSerializer(user)
		return Response(serializer.data)


class GetUser(APIView):
	permission_classes = [permissions.AllowAny]
	def get(self,request):
		if request.user.is_authenticated:
			serializer=UserSerializer(request.user)
			return Response(serializer.data)
		return Response({'message':'unlogged'})

class IsvendeurActive(APIView):
	permission_classes = [permissions.AllowAny]
	def get(self,request):
		if request.user.is_authenticated:
			vendeur=request.user
			if vendeur.active==True:
				return Response(True)
			return Response(False)
		return Response(False)


class ModificationCredential(ModelViewSet):
	queryset = User.objects.filter(active=True)
	serializer_class=UserSerializer
	@action(methods=["put"], detail=False, url_path='modif')
	def modif_cred(self,request,*args,**kwargs):
		user=self.request.user
		data=request.data
		user.nom=data['nom']
		user.phone=data['phone']
		user.prenom=data['prenom']
		user.save()
		return Response({'message':'donnee bien modifiee'})


class HandleNotif(ModelViewSet):
	queryset = Notification.objects.all()
	serializer_class=NotificationSerializer

	@action(methods=["put"], detail=False, url_path='handlenotif')
	def lunotif(self,request):
		user=self.request.user
		notification=Notification.objects.filter(user=user,lu=False)
		for n in notification:
			n.lu=True
			n.save()
		return Response({'message':'donnee bien modifiee'})
		


		
		
		
		


