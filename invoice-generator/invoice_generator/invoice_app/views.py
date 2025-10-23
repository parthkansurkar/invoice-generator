from django.shortcuts import render

# Create your views here.
def template_selection(request):
    document_type = "invoice"
    return render(request, "template_selection.html", {"document_type": document_type})
