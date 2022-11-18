from django.conf import settings
#import settings
import sys
sys.path.append('../../../common')


def dev(request):
    """dev.

    Args:
        request:
    """
    return {'WEB_DOMAIN': settings.WEB_DOMAIN}


def cfg_assets_root(request):
    return {'ASSETS_ROOT': settings.ASSETS_ROOT}
