from django.shortcuts import render

def contrib_file(request):
  return render(request,'dpaste/contribute.html')
