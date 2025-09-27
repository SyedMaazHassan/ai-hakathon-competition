from django.conf import settings

def project_details(request):
    return {
        'PROJECT_NAME': settings.PROJECT_NAME
    }
