from django.shortcuts import render

def menu_docente(request):
    return render(request, "menuDocente.html")
