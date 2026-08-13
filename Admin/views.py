from django.shortcuts import render

from Detector.models import Detector

# Create your views here.

def adminHome(request):
    if not request.session.get('admin'):
        return render(request,'adminLogin.html')    
    return render(request,'admin/adminHome.html')


def admin_Login(request):
    if request.method=="POST":
        loginid=request.POST['loginId']
        password=request.POST['password']

        if loginid=="admin" and password=='admin':
            request.session['admin']=True
            return render(request,'admin/adminHome.html')
        else:
            messages.error(request,'Invalid details')
            return render(request,'adminLogin.html')
    else:
        return render(request,'adminLogin.html')

def user_details(request):
    if not request.session.get('admin'):
        return render(request,'adminLogin.html')
    users=Detector.objects.all()
    return render(request,'admin/userDetails.html',{'users':users})

def log(request):
    request.session.flush()  # clears all session data
    return render(request,'index.html')


from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

def activate_user(request):

    id=request.GET['id']
    user = get_object_or_404(Detector, id=id)
    user.status = 'Active'
    user.save()
    users=Detector.objects.all()
    return render(request,'admin/userDetails.html',{'users':users})  # Change 'user_list' to your actual template/view name

def deactivate_user(request):
    id=request.GET['id']
    user = get_object_or_404(Detector, id=id)
    user.status = 'Inactive'
    user.save()
    users=Detector.objects.all()
    return render(request,'admin/userDetails.html',{'users':users})