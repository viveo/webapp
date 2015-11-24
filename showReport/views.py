from django.shortcuts import render, render_to_response
from showReport.models import *
from rest_framework import viewsets
from showReport.serializers import *
import csv
import os
from showReport.forms import UploadFileForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
import csv_validator
# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows reports to be viewed or edited.
    """
    queryset = ReportTable.objects.all()
    serializer_class = ReportSerializer

class AssetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows reports to be viewed or edited.
    """
    queryset = AssetRating.objects.all()
    serializer_class = AssetSerializer

def mainMenu(request):
    context=AssetRating.objects.all()
    return render(request, 'mainMenu.html', {"context":context.values()})


def getAssets(request):
    validationMessage = ""
    validateResult = 0
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            validateResult, validationMessage = csv_validator.validateCSV(request.FILES['csvFile'])
    else:
        form = UploadFileForm() # empty
    context=AssetRating.objects.all()
    return render_to_response('assetData.html', 
        {"context":context.values(), 'form': form, "validationMessage": validationMessage},
        context_instance=RequestContext(request))

def home(request):
    # workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
    # resultlist = []
    # with open(workpath+'/static/webapp_input.csv', 'rt') as f:
    #     reader = csv.DictReader(f)
    #     for row in reader:
    #         resultlist.append(row)
    # context=AssetRating.objects.all()
    # print context.values()
    return render(request, 'home.html')