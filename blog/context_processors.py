from django.conf import settings

from .models import Category


def icp_info(request):
    return {
        'ICP_INFO': getattr(settings, 'ICP_INFO', ''),
        'GOV_INFO': getattr(settings, 'GOV_INFO', '')
    }


def categories(request):
    return {
        'categories': Category.objects.all()
    }
