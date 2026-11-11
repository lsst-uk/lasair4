"""Tests for the survey logo in the site sidebar template."""
from typing import Tuple

from django.test import SimpleTestCase

ASSETS_ROOT = '/lasair/static'
ZTF_LOGO_SRC = ASSETS_ROOT + '/img/brand/ztf_logo_dark_bg.png'
ZTF_LOGO_ALT_ATTR = 'alt="Zwicky Transient Facility (ZTF) logo"'
LASAIR_LOGO_SRC = ASSETS_ROOT + '/img/brand/logo_light.svg'
DESKTOP_SIDEBAR_MARKER = 'id="sidebarMenu"'


def render_sidebar() -> Tuple[str, str]:
    """*render the sidebar include as an anonymous visitor on the home page*

    **Return:**

    - ``mobileNavbar`` -- the HTML before the desktop sidebar (the mobile navbar)
    - ``desktopSidebar`` -- the HTML of the desktop sidebar

    **Usage:**

        mobileNavbar, desktopSidebar = render_sidebar()
    """
    from django.contrib.auth.models import AnonymousUser
    from django.template.loader import render_to_string
    from django.test import RequestFactory

    request = RequestFactory().get('/')
    request.user = AnonymousUser()
    context = {
        'ASSETS_ROOT': ASSETS_ROOT,
        'docroot': '',
        'request': request,
        'user': request.user,
    }
    html = render_to_string('includes/sidebar.html', context)
    splitAt = html.index(DESKTOP_SIDEBAR_MARKER)
    return html[:splitAt], html[splitAt:]


class SidebarSurveyLogoTest(SimpleTestCase):
    """*check the ZTF logo shows below the Lasair logo in the mobile navbar and the desktop sidebar*"""

    def test_shows_one_ztf_logo_in_mobile_navbar(self) -> None:
        # ACT
        mobileNavbar, _ = render_sidebar()

        # ASSERT
        self.assertEqual(mobileNavbar.count(ZTF_LOGO_SRC), 1)
        self.assertEqual(mobileNavbar.count(ZTF_LOGO_ALT_ATTR), 1)

    def test_shows_one_ztf_logo_in_desktop_sidebar(self) -> None:
        # ACT
        _, desktopSidebar = render_sidebar()

        # ASSERT
        self.assertEqual(desktopSidebar.count(ZTF_LOGO_SRC), 1)
        self.assertEqual(desktopSidebar.count(ZTF_LOGO_ALT_ATTR), 1)

    def test_ztf_logo_sits_below_lasair_logo_in_desktop_sidebar(self) -> None:
        # ACT
        _, desktopSidebar = render_sidebar()

        # ASSERT
        self.assertLess(desktopSidebar.index(LASAIR_LOGO_SRC), desktopSidebar.index(ZTF_LOGO_SRC))
