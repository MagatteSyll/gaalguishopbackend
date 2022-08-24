
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views
from user.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',index),
    path('api/utilisateur/',include('user.urls')),
    path('api/produit/',include('produit.urls')),
    #path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls')),
    path('api/staff/',include('staff.urls'))


]

#urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns +=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
