# -*- coding: utf-8 -*-
import urllib
import time
import datetime
import pytz
import smtplib
import uuid
import types
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email.Header import Header
from zope.interface import implements
from zope.catalog.catalog import Catalog
from zope.catalog.field import FieldIndex
from zope.catalog.text import TextIndex
from zope.catalog.keyword import CaseInsensitiveKeywordIndex
from Acquisition import aq_parent
from cornerstone.soup.interfaces import ICatalogFactory
from cornerstone.soup import getSoup
from cornerstone.soup import Record
from cornerstone.soup.ting import TingIndex
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

def ordernumber():
    onum = hash(time.time())
    if onum < 0:
        return '0%s' % str(abs(onum))
    return '1%s' % str(onum)

class BookingsCatalogFactory(object):

    implements(ICatalogFactory)

    def __call__(self):
        catalog = Catalog()
        catalog[u'recordtype']    = FieldIndex(field_name='recordtype',
                                               field_callable=False)
        catalog[u'creator']       = FieldIndex(field_name='creator',
                                               field_callable=False)
        catalog[u'uid']           = FieldIndex(field_name='uid',
                                               field_callable=False)
        catalog[u'created']       = FieldIndex(field_name='created',
                                               field_callable=False)
        catalog[u'deliverable']   = FieldIndex(field_name='deliverable',
                                               field_callable=False)
        catalog[u'exported']      = FieldIndex(field_name='exported',
                                               field_callable=False)
        catalog[u'title']         = FieldIndex(field_name='title',
                                               field_callable=False)
        catalog[u'ordernumber']   = FieldIndex(field_name='ordernumber',
                                               field_callable=False)
        catalog[u'bookingnumber'] = FieldIndex(field_name='bookingnumber',
                                               field_callable=False)
        catalog[u'distributor']   = FieldIndex(field_name='distributor',
                                               field_callable=False)
        catalog[u'searchable']    = TingIndex(('fullname',
                                               'city',
                                               'ordernumber'),
                                              field_callable=False)
        return catalog

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
    
    def distributor(self, item):
        """Return brain of item distributor.
        """
        brain = self.itembrain(item)
        if not brain:
            return None
        obj = brain.getObject()
        return aq_parent(obj)
    
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

class Orders(object):
    """XXX move order processing functions of checkout form here.
    """
    
    def __init__(self, context):
        self.context = context
        self.soup = getSoup(self.context, u'bda_broschuerenshop_bookings')
    
    def add(self, defs):
        defs['recordtype'] = 'order'
        self.soup.add(Record(**defs))
    
    def orders(self, **kw):
        kw['recordtype'] = 'order'
        return self.soup.query(**kw)
    
    def lazy(self, **kw):
        kw['recordtype'] = 'order'
        return self.soup.lazy(**kw)

class Stock(object):
    """Manage stock.
    """
    
    def __init__(self, context):
        self.context = context
        self.iteminfo = ItemInfo(context)
    
    def stock(self, uid, preorderedcount=0):
        brain = self.iteminfo.itembrain((uid, None))
        if brain is None:
            return 0
        return int(brain.getLagerbestand) - preorderedcount
    
    def setstock(self, item):
        """Set stock of article with 'uid' with 'count'.
        
        @param item: 2-tuple containing (uid, count)
        """
        info = self.iteminfo
        article = info.itembrain(item).getObject()
        article.setLagerbestand(item[1])
        article.reindexObject()
        info.cat.reindexObject(article, idxs=['id'], update_metadata=1)
    
    def reducestock(self, item):
        """Reduce stock of article with 'uid' by 'count'.
        
        @param item: 2-tuple containing (uid, count)
        """
        info = self.iteminfo
        articlebrain = info.itembrain(item)
        if not articlebrain:
            # the rare case if an article was deleted before the order was 
            # downloaded
            return
        article = articlebrain.getObject()
        article.setLagerbestand(article.getLagerbestand() - item[1])
        article.reindexObject()
        info.cat.reindexObject(article, idxs=['id'], update_metadata=1)
    
    def increasestock(self, item):
        """Increase stock of article with 'uid' by 'count'.
        
        @param item: 2-tuple containing (uid, count)
        """
        info = self.iteminfo
        article = info.itembrain(item).getObject()
        article.setLagerbestand(article.getLagerbestand() + item[1])
        article.reindexObject()
        info.cat.reindexObject(article, idxs=['id'], update_metadata=1)
    
    def deliverable(self, item, preorderedcount):
        """Check if 'count' articles with 'uid' are deliverable.
        
        @param item: 2-tuple containing (uid, count)
        @param preorderedcount: int with number of already preordered
        """
        return (self.stock(item[0], preorderedcount) - item[1]) > 0  

class Bookings(Stock):
    """Bookings manager.
    """
    
    def __init__(self, context):
        self.context = context
        self.soup = getSoup(self.context, u'bda_broschuerenshop_bookings')
        Stock.__init__(self, self.context)
    
    def add(self, defs):
        """Create Record from defs and add to bookings soup.
        
        @param defs: dict containing the item definitions.
        """
        defs['bookingnumber'] = str(uuid.uuid4())
        defs['exported'] = FLOORDATETIME
        item = (defs['uid'], defs['count'])
        defs['deliverable'] = self.deliverable(item, 
                                             self.count_unexported(defs['uid']))
        defs['recordtype'] = 'booking'
        record = Record(**defs)
        self.soup.add(record)      
    
    def bookings(self, **kw):
        """generic query for bookings, given kwargs are used a query args."""
        kw['recordtype'] = 'booking'
        return self.soup.query(**kw)
    
    def lazy(self, **kw):
        kw['recordtype'] = 'booking'
        return self.soup.lazy(**kw)
    
    def unexported(self, distributor):
        """all bookings for distributor not exported in past.""" 
        return self.bookings(exported=FLOORDATETIME, distributor=distributor,
                             deliverable=True)
    
    def count_unexported(self, uid):
        """number of bookings on an item which were not exported so far."""
        count = 0
        for record in self.bookings(exported=FLOORDATETIME, uid=uid, 
                                    deliverable=True):
            count += record.count
        return count
    
    def check_nondeliverables(self):
        """checks all as undeliverable marked bookings. if its deliverable 
        meanwhile, unmark it."""  
        records = self.bookings(exported=FLOORDATETIME, deliverable=False)
        for record in records:
            item = (record.uid, record.count)
            if not self.deliverable(item, self.count_unexported(record.uid)):
                continue
            record.data['deliverable'] = True
            self.soup.reindex([record])     
            
    def exported(self, start, end, distributor):
        """all exported bookings of a given range for a given distributor"""
        return self.bookings(exported=(start, end), distributor=distributor)   
        
    def anonymonize(self, border):
        """Make orders anonymous which are older than given border-date.
        """
        # XXX TODO
        pass

"""MAIL_SUBJECT

Erwartet Shopnamen als format Parameter.
"""
#MAIL_SUBJECT = u'Ihre Bestellung bei %s'

"""MAIL_BODY

* gender - Herr/Frau
* name - Kundenname
* domain - Shop domain
* orderid - Bestellnummer base64 encoded
* email - E-Mail Adresse
* rescueaddress - E-Mail Adresse für Reklamationen
* signature - E-Mail Signatur
* ordertext - Bestelltext
* anschrifttext - Anschrift, Lieferanschrift

"""
#MAIL_BODY = """Sehr geehrte/r %(gender)s %(name)s:
#
#Vielen Dank für Ihre Bestellung.
#
#Die Bestellnummer lautet: %(orderid)s
#
#Auflistung Ihrer Bestellung:
#%(ordertext)s
#
#Sollte diese Bestellung nicht von Ihnen getätigt worden sein, schicken Sie
#bitte umgehend eine Benachrichtigung an %(rescueaddress)s.
#
#Mit freundlichen Grüßen
#
#%(signature)s 
#"""

MAIL_SUBJECT = u'Ihre Bestellung beim Bankenverband'

"""MAIL_BODY
* date
* orderid
* delivery_address
* ordertext
"""
MAIL_BODY = """Bundesverband deutscher Banken

Bestätigung Ihrer Bestellung vom %(date)s, Kunden-ID: %(orderid)s
--------------------------------------------------------------------------------

Herzlichen Dank für Ihr Interesse an unseren Publikationen.
Ihre Bestellung wird so schnell wie möglich ausgeführt.

Folgende Daten wurden aufgenommen:

Lieferanschrift:%(delivery_address)s

Ihre Bestellung:
%(ordertext)s
Hier finden Sie unsere "Hinweise zur online Bestellung". Diese enthalten
für den Fall einer entgeltpflichtigen Broschüren-Bestellung auch die
Belehrung über Ihr Widerrufsrecht nach Fernabsatzrecht (§§ 312 b ff. BGB).

Hinweise zur online Bestellung
https://www.bankenverband.de/publikationen/bestellhinweise/hinweise-zur-online-bestellung

Mit freundlichen Grüßen,
Ihr Bankenverband

Bundesverband deutscher Banken
Postfach 04 03 07
Telefon: 030 / 1663 - 0
Telefax: 030 / 1663 - 1298
e-Mail: bankenverband@bdb.de
"""

class MailNotify(object):
    """Object for performing mail notifications.
    """
    
    def __init__(self, context):
        self.context = context
    
    def send(self, subject, message, receiver):
        if self.context.REQUEST.get('_mail_already_sent') == 1:
            return True
        purl = getToolByName(self.context, 'portal_url')
        mailfrom = purl.getPortalObject().email_from_address
        mailhost = getToolByName(self.context, 'MailHost')
        subject = subject.encode('utf-8')
        subject = Header(subject, 'utf-8')
        message = message.encode('UTF-8')
        message = MIMEText(message, _subtype='plain')
        message.set_charset('utf-8')
        message.add_header('Date',  formatdate(localtime=True))
        message.add_header('From_', mailfrom)
        message.add_header('From', mailfrom)
        message.add_header('To', receiver)
        message['Subject'] = subject
        server = mailhost.smtp_host
        port = mailhost.smtp_port
        user = mailhost.smtp_userid
        passwd = mailhost.smtp_pass
        server = smtplib.SMTP(server, port)
        server.login(user, passwd)
        server.set_debuglevel(0)
        from_ = message['From_']
        message = message.as_string()
        server.sendmail(from_, receiver, message)
        server.quit()
        self.context.REQUEST['_mail_already_sent'] = 1
        return True