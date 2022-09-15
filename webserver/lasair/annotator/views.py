from django.shortcuts import render
from .models import Annotators


def annotators(request):
    anns = Annotators.objects.filter().order_by('topic')
    annotators = []
    for a in anns:
        d = {
            'usersname': a.user.first_name + ' ' + a.user.last_name,
            'topic': a.topic,
            'description': a.description
        }
        annotators.append(d)

    return render(request, 'annotators.html', {'annotators': annotators})
