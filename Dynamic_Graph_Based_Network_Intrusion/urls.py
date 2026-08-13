"""
URL configuration for Dynamic_Graph_Based_Network_Intrusion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views as mv
from Admin import views as av
from Detector import views as dv

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',mv.index,name='index'),
    path('detector_LoginForm',mv.detector_LoginForm,name='detector_LoginForm'),
    path('admin_LoginForm',mv.admin_LoginForm,name='admin_LoginForm'),
    path('detector_registerForm',mv.detector_registerForm,name='detector_registerForm'),
    path('aboutus',mv.aboutus,name='aboutus'),



    path('admin_Login',av.admin_Login,name='admin_Login'),
    path('adminHome',av.adminHome,name='adminHome'),
    path('user_details',av.user_details,name='user_details'),
    path('log',av.log, name='log'),
    path('activate_user', av.activate_user, name='activate_user'),
    path('deactivate_user', av.deactivate_user, name='deactivate_user'),



    path('detector_register',dv.detector_register,name='detector_register'),
    path('detector_login',dv.detector_login,name='detector_login'),
    path('DetectorHome',dv.DetectorHome,name='DetectorHome'),
    path('training',dv.training,name='training'),
    path('prediction',dv.prediction,name='prediction'),
    

    

]
