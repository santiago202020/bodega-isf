from django.shortcuts import render
from login.decorators import login_required_custom

@login_required_custom
def menu_view(request):
    return render(request, "menu.html")
