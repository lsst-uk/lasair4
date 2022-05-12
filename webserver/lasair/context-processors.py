import sys
sys.path.append('../../../common')
import settings

def dev(request):
    """dev.

    Args:
        request:
    """
    return {'WEB_DOMAIN': settings.WEB_DOMAIN}
