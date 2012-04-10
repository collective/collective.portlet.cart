import urllib
from zope.interface import (
    Interface,
    Attribute,
    implements,
)
from zope.component import adapts
from zope.publisher.interfaces.browser import IBrowserRequest


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


class ICartDataProvider(Interface):
    
    data = Attribute(u"Cart data as list of dicts.")
    
    disable_max_article = Attribute(u"Flag whether to disable max article "
                                    u"limit.")
    
    show_summary = Attribute(u"Flag whether to show cart summary.")
    
    summary_total_only = Attribute(u"Flag whether to show total sum only in "
                                   u"summary.")
    
    checkout_url = Attribute(u"URL to checkout view.")
    
    cart_url = Attribute(u"URL to cart view.")
    
    def validate_count(uid, count):
        """Validate if ordering n items of UID is allowed.
        """


class CartDataProviderBase(object):
    implements(ICartDataProvider)
    adapts(Interface, IBrowserRequest)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    @property
    def disable_max_article_count(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``disable_max_article_count``.")
    
    @property
    def show_summary(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``show_summary``.")
    
    @property
    def summary_total_only(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``summary_total_only``.")
    
    @property
    def checkout_url(self):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``checkout_url``.")
    
    @property
    def cart_url(self):
        return '%s/@@cart' % self.context.absolute_url()
    
    def validate_count(self, uid, count):
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``validate_count``.")
    
    def net(self, items):
        """Calculate net sum of cart items.
        """
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``net``.")
    
    def vat(self, items):
        """Calculate vat sum of cart items.
        """
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``vat``.")
    
    def cart_items(self, items):
        """Return list of dicts with format returned by ``self.item``.
        """
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``cart_items``.")
    
    def item(self, uid, title, count, price, url):
        """
        @param uid: catalog uid
        @param title: string
        @param count: item count as int
        @param price: item price as float
        @param url: item URL
        """
        return {
            'cart_item_uid': uid,
            'cart_item_title': title,
            'cart_item_count': count,
            'cart_item_price': self._ascur(price),
            'cart_item_location:href': url,
        }
    
    @property
    def data(self):
        ret = {
            'cart_items': list(),
            'cart_summary': dict(),
        }
        items = extractitems(self.request.form.get('items'))
        if items:
            net = self.net(items)
            vat = self.vat(items)
            cart_items = self.cart_items(items)
            ret['cart_items'] = cart_items
            ret['cart_summary']['cart_net'] = self._ascur(net)
            ret['cart_summary']['cart_vat'] = self._ascur(vat)
            ret['cart_summary']['cart_total'] = self._ascur(net + vat)
            ret['cart_summary']['cart_total_raw'] = net + vat
        return ret
    
    def _ascur(self, val):
        val = '%.2f' % val
        return val.replace('.', ',')