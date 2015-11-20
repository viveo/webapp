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
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            inputData = csv.reader(request.FILES['csvFile'])
            ipSets = set()
            for _ in xrange(8):
                next(inputData)
            for line in inputData:
                ip = line[0]
                if ip in ipSets: continue
                ipSets.add(ip)
            for curIP in ipSets:
                if AssetRating.objects.filter(ip=curIP).count() == 0:
                    newAsset = AssetRating(ip=curIP, rating=5)
                    try:
                        newAsset.save()
                    except:
                        print "Cannot save" + newAsset.ip + "!"  
    else:
        form = UploadFileForm() # empty
    context=AssetRating.objects.all()
    return render_to_response('assetData.html', 
        {"context":context.values(), 'form': form},
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