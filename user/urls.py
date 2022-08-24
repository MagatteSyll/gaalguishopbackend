from django.urls import path,include
from .views import*
from rest_framework.routers import SimpleRouter
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet



router=SimpleRouter()
router.register('modifcred',ModificationCredential)
router.register('handlenotify',HandleNotif)
router.register('suspensioninscription',SuspensionUserRegistration)



urlpatterns=[
    path('',include(router.urls)),
    path('phonecodeconfirmation/',PhoneConfirmationRegistration.as_view()),
    path('registration/',RegistrationView.as_view()),
    path('connexion/',MyTokenObtainPairView.as_view()),
    path('token/refresh/', MyTokenRefreshPairView.as_view(), name='token_refresh'),
    path('isauthenticated/',Authent.as_view()),
    path('getuser/',GetUser.as_view()),
    path('isactive/',IsvendeurActive.as_view()),
    path('getchannel/',GetUserChannel.as_view()),
    path('getnotification/',GetNotifications.as_view()),
    path('getnewuser/',GetNewUser.as_view()),
    path('getbadge/', GetBadgeNotif.as_view()),
    path('getuseregistration/',GetuserRegistration.as_view()),
    path('getdeviceapp/', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'})),
    
   
      
    





]