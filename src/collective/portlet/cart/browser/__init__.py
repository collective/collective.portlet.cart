import simplejson as json
from zope.interface import implements
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.memoize import instance
from collective.portlet.cart import ICartDataProvider


class CartView(BrowserView):
    """View for cart.
    """
    
    @property
    def show_summary(self):
        return True


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


class ICartPortlet(IPortletDataProvider):
    pass


class CartAssignment(base.Assignment):
    implements(ICartPortlet)

    @property
    def title(self):
        return _(u"Cart")


class CartRenderer(base.Renderer):
    
    template = ViewPageTemplateFile('portlet.pt')

    def update(self):
        url = self.context.restrictedTraverse('@@plone').getCurrentUrl()
        if url.endswith('@@cart') \
          or url.find('@@checkout') != -1 \
          or url.find('@@confirm_order') != -1 \
          or url.find('/portal_factory/') != -1:
            self.show = False
        else:
            self.show = True
    
    def render(self):
        if not self.show:
            return u''
        return self.template()
    
    @property
    @instance.memoize
    def disable_max_article_count(self):
        member = self.context.portal_membership.getAuthenticatedMember()
        return not member.has_role('Anonymous')


class CartAddForm(base.NullAddForm):
    label = _(u"Add Cart Portlet")
    description = _(u"This portlet displays the shopping cart.")

    def create(self):
        return CartAssignment()