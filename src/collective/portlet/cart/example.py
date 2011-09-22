from collective.portlet.cart import CartDataProviderBase

class ExampleCartDataProvider(CartDataProviderBase):
    
    # dummy uids from example.pt to price mapping
    PRICES = {
        '12345678': 2,
        '12345679': 5.99,
        '12345680': 8.50,
        '12345681': 15,
    }
    
    def net(self, items):
        p = 0
        for item in items:
            p += self.PRICES[item[0]] * item[1]
        return p
    
    def vat(self, items):
        return self.net(items) * 0.2
    
    def cart_items(self, items):
        ret = list()
        for item in items:
            uid = item[0]
            title = 'Artikel %s' % uid
            count = item[1]
            price = self.PRICES[uid] * count
            url = self.context.absolute_url()
            ret.append(self.item(uid, title, count, price, url))
        return ret        
    
    def validate_count(self, uid, count):
        return True
    
    @property
    def disable_max_article(self):
        return False
    
    @property
    def show_summary(self):
        return True
    
    @property
    def summary_total_only(self):
        return False
    
    @property
    def checkout_url(self):
        return '%s/@@checkout' % self.context.absolute_url()