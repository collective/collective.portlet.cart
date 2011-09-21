import simplejson as json
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from collective.portlet.cart import ICartDataProvider

class CartDataView(BrowserView):
    """JSON view for cart.
    """

    @property
    def data_provider(self):
        return getMultiAdapter(
            (self.context, self.request), ICartDataProvider)
    
    def validateItemCount(self):
        uid = self.request.form.get('uid'),
        count = int(self.request.form.get('count')),
        return json.dumps(self.data_provider.validate_count(uid, count))
    
    def cartData(self):
        return json.dumps(self.data_provider.data)