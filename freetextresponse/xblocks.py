"""
This is the core logic for the XBlock
"""
from __future__ import absolute_import
from xblock.core import XBlock

from .mixins.scenario import XBlockWorkbenchMixin
from .mixins.user import MissingDataFetcherMixin
from .models import FreeTextResponseModelMixin
from .views import FreeTextResponseViewMixin


@XBlock.needs('i18n')
class FreeTextResponse(
        FreeTextResponseModelMixin,
        FreeTextResponseViewMixin,
        MissingDataFetcherMixin,
        XBlockWorkbenchMixin,
        XBlock,
):
    """
    A fullscreen image modal XBlock.
    """
