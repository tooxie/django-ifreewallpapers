from django.conf import settings

def urls(request):
    return {'IMG_URL': settings.IMG_URL, 'CSS_URL': settings.CSS_URL,
            'JS_URL': settings.JS_URL, 'MEDIA_URL': settings.MEDIA_URL}

def language(request):
    try:
        lang = settings.LANGUAGE_CODE[:settings.LANGUAGE_CODE.index('-')]
    except:
        lang = settings.LANGUAGE_CODE
    return {'LANGUAGE': lang}
