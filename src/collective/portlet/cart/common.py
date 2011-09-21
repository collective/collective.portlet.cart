import urllib
import datetime
import pytz
from Acquisition import aq_parent
from Products.CMFPlone.utils import getToolByName


FLOORDATETIME = datetime.datetime(1980, 1, 1, tzinfo=pytz.timezone('UTC'))


def message(context, msg):
    putils = getToolByName(context, 'plone_utils')
    putils.addPortalMessage(msg)


def readcookie(request):
    """Read, unescape and return the cart cookie.
    """
    return urllib.unquote(request.cookies.get('cart', ''))


def deletecookie(request):
    """Delete the cart cookie.
    """
    request.response.expireCookie('cart', path='/')


def extractitems(items):
    """Cart items are stored in a cookie. The format is
    ``uid:count,uid:count,...``.
    
    Return a list of 2-tuples containing ``(uid, count)``.
    """
    if not items:
        return []
    ret = list()
    items = items.split(',')
    for item in items:
        if not item:
            continue
        item = item.split(':')
        ret.append((item[0], int(item[1])))
    return ret


class ItemInfo(object):
    """Object providing item info.
    """
    
    def __init__(self, context):
        self.context = context
    
    def itembrain(self, item):
        """Return brain for item defs.
        """
        brains = self.cat(UID=item[0])
        if brains:
            return brains[0]
        return None
    
    @property
    def cat(self):
        if not hasattr(self, '_cat'):
            self._cat = getToolByName(self.context, 'portal_catalog')
        return self._cat


class Calculator(ItemInfo):
    """Object to calculate item pricing.
    """
    
    def calcitems(self, items):
        """Calculate the price for items.
        
        Accept a list of item definitions to calculate netto and ust.
        
        @param items: list of 2-tuples containing (object_uid, count)
        @return: 2-tuple containing (netto, ust)
        """
        sum_netto = 0.0
        sum_ust = 0.0
        for item in items:
            netto, ust = self.calcitem(item)
            sum_netto += netto
            sum_ust += ust
        return (sum_netto, sum_ust)
    
    def calcitem(self, item):
        """Calculate the price for item.
        
        Accept a single item definition to calculate netto and ust.
        
        @param item: 2-tuple containing (object_uid, count)
        @return: 2-tuple containing (netto, ust)
        """
        brain = self.itembrain(item)
        count = item[1]
#        netto = float(brain.getPreis)
        netto = 128
#        ust = netto * (float(brain.getUst) * 0.01)
        ust = 3.5
        return (netto * count, ust * count)