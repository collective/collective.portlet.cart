=======================
collective.portlet.cart
=======================

Shopping cart portlet for plone.


Installation
------------

Depend your instance to ``collective.portlet.cart`` and install it as addon
in plone control panel.

Test if it works by navigating to ``http://your.site/cartexample``.


Provide data
------------

This package only provides components needed to render shopping cart. It does
not expect any contracts but ``collective.portlets.cart.ICartDataProvider``.

Implement data provider inheriting from
``collective.portlets.cart.CartDataProviderBase``,

::

    >>> from collective.portlet.cart import CartDataProviderBase
    >>> class AppCartDataProvider(CartDataProviderBase):
    ...     """Also look at ``collective.portlets.cart.example`` source code.
    ...     """
    ...     
    ...     def net(self, items):
    ...         """Return net price for items as float.
    ...         Items is a list of 2-tuples containing (uid, count).
    ...         
    ...         See ``collective.portlets.cart.example``
    ...         """
    ...     
    ...     def vat(self, items):
    ...         """Return VAT for items as float.
    ...         Items is a list of 2-tuples containing (uid, count).
    ...         """
    ...     
    ...     def cart_items(self, items):
    ...         """Return list of dicts with format returned by ``self.item``.
    ...         """  
    ...     
    ...     def validate_count(self, uid, count):
    ...         """Validate if ordering n items of UID is allowed.
    ...         """
    ...     
    ...     @property
    ...     def disable_max_article(self):
    ...         """Flag whether to disable max article limit.
    ...         """
    ...     
    ...     @property
    ...     def show_summary(self):
    ...         """Flag whether to show cart summary.
    ...         """
    ...     
    ...     @property
    ...     def summary_total_only(self):
    ...         """Flag whether to show total sum only in summary.
    ...         """
    ...         return False
    ...     
    ...     @property
    ...     def checkout_url(self):
    ...         """URL to checkout view.
    ...         """
    ...         return '%s/@@checkout' % self.context.absolute_url()
    ...     
    ...     @property
    ...     def cart_url(self):
    ...         """URL to cart view.
    ...         """
    ...         return '%s/@@cart' % self.context.absolute_url()

and register it as adapter with ZCML. The adapter is looked up for context
and request, these attributes are available on ``context`` respective
``request`` on data provider::

    <adapter
        for="some.package.IContext
             zope.publisher.interfaces.browser.IBrowserRequest"
        factory="some.package.AppCartDataProvider" />


Markup
------

Take a look at ``collective.portlets.cart.browser:example.pt`` how HTML markup
for adding items to cart might look like.

Basically a shop item consists of a container DOM element, containing an
element with CSS class ``cart_item_uid``, where the item UID is taken from,

::

    <span class="cart_item_uid" style="display: none;">12345678</span>

a text input field with CSS class ``cart_item_count`` which is read for
item count,

::

    <input type="text" size="2" value="1" class="cart_item_count" />Stück

the "add to Cart" action,

::

    <a href="" class="add_cart_item">add to cart</a>

and the "update cart" avtion.

::

    <a href="" class="update_cart_item">update cart</a>


Javascript
----------

The cart can be customizes on client side.

Flag whether to hide cart container if cart is empty::

    CART_HIDE_CONTAINER_IF_EMPTY = [true|false];

Maximum number of allowed articles in order::

    CART_MAX_ARTICLE_COUNT = 20;

Client side dislog messages::

    cart.messages['article_limit_reached'] = "Article limit reached";
    cart.messages['total_limit_reached'] = "Total limit reached";
    cart.messages['not_a_number'] = "Input not a number";


Contributors
------------

- Robert Niederreiter

- Peter Holzer

- Sven Plage

- Icons by famfamfam


History
-------

0.9dev
------

- initial
