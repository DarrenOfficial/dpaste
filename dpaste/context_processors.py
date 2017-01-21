from django.conf import settings

def dpaste_globals(request):
    return {
        'site_name': getattr(settings, 'DPASTE_SITE_NAME', 'dpaste.de'),
        'jquery_url': getattr(settings, 'DPASTE_JQUERY_URL',
            'https://ajax.googleapis.com/ajax/libs/jquery/1/jquery.js'),
    }
