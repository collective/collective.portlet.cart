import simplejson as json
from zope.interface import Interface, Attribute, implements
from zope.component import adapts, getMultiAdapter
from zope.publisher.interfaces.browser import IBrowserRequest
from Products.Five import BrowserView
from collective.portlet.cart.common import extractitems, Calculator, ItemInfo


class ICartDataProvider(Interface):
    
    data = Attribute(u"Cart data as json response")


class CartDataProvider(object):
    """collective.portlet.cart item provider.
    """
    
    implements(ICartDataProvider)
    adapts(Interface, IBrowserRequest)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    @property
    def rawdata(self):
        ret = {
            'cart_items': list(),
            'cart_summary': dict(),
        }
        items = extractitems(self.request.form.get('items'))
        if items:
            calculator = Calculator(self.context)
            for item in items:
                brain = calculator.itembrain(item)
                if not brain:
                    continue
                url = '%s/shopitem/%s' % (self.context.absolute_url(),
                                          brain.UID)
                netto, ust = calculator.calcitem(item)
                ret['cart_items'].append({
                    'cart_item_uid': brain.UID,
                    'cart_item_title': brain.Title,
                    'cart_item_count': item[1],
                    'cart_item_price': self._ascur(netto + ust),
                    'cart_item_location:href': url,
                })
            sum_netto, sum_ust = calculator.calcitems(items)
            ret['cart_summary']['cart_netto'] = self._ascur(sum_netto)
            ret['cart_summary']['cart_ust'] = self._ascur(sum_ust)
            ret['cart_summary']['cart_total'] = self._ascur(sum_netto + sum_ust)
            ret['cart_summary']['cart_total_raw'] = sum_netto + sum_ust
        return ret
    
    @property
    def data(self):
        return json.dumps(self.rawdata)
    
    def _ascur(self, val):
        val = '%.2f' % val
        return val.replace('.', ',')


class CartDataView(BrowserView):
    """JSON view for the cart.
    """

    def validateItemCount(self):
        member = self.context.portal_membership.getAuthenticatedMember()
        if not member.has_role('Anonymous'):
            return json.dumps(True)
        item = (
            self.request.form.get('uid'),
            int(self.request.form.get('count')),
        )
        max = ItemInfo(self.context).itembrain(item).getMaxbestellmenge
        if item[1] > max:
            return json.dumps(False)
        return json.dumps(True)
    
    def cartData(self):
        return getMultiAdapter((self.context, self.request),
                               ICartDataProvider).data