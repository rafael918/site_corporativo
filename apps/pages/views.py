from pyexpat.errors import messages
from django.shortcuts import render

# Create your views here.
def index(request):
    context = {
        
    'messagem' : messages.sucess(request, 'Esta é uma mensagem de sucess!')
    
    }
    return render(request, 'index.html', context)
