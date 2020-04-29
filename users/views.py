from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect


def login_page(request):
    if request.method == "POST":
        username = request.POST.get('login')
        password = request.POST.get('password')

        if username is not None and password is not None:
            user = authenticate(request=request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('/')

    return render(request, template_name='users/login.html')
