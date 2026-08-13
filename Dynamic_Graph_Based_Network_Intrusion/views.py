

from django.shortcuts import render


def index(request):
    return render(request,'index.html')


def detector_LoginForm(request):
    return render(request,'detector_LoginForm.html')


def admin_LoginForm(request):
    return render(request,'adminLogin.html')

def detector_registerForm(request):
    return render(request,'detector_registerForm.html')


def aboutus(request):
    return render(request,'aboutus.html')