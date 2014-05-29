import klarnacheckout

import logging
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from Products.Five import BrowserView
from bda.plone.orders.common import get_order
from bda.plone.payment import (
                               Payment,
                               Payments,
                               )

from bda.plone.payment.interfaces import IPaymentData
from bda.plone.shop.interfaces import IShopSettings

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from bda.plone.klarnapayment import IKlarnaPaymentSettings

_ = MessageFactory('bda.plone.klarnapayment')
logger = logging.getLogger('bda.plone.payment')


import klarnacheckout

class Klarna(Payment):
    pid = 'klarna'
    label = _('klarna', 'Klarna')
    
    def init_url(self, uid):
        return '%s/@@klarna_payment?uid=%s' % (self.context.absolute_url(), uid)


class KlarnaPay(BrowserView):
    """
    Assembles an url to dibs.
    Need to check how to use (in lin 109)
    make_query() 
    """

    def __call__(self, **kw):
        uid = self.request['uid']
        base_url = self.context.absolute_url()
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IKlarnaPaymentSettings)
        
        pdata = IPaymentData(self.context).data(uid)
        
        amount = pdata['amount']
        currency = pdata['currency']
        description = pdata['description']
        ordernumber = pdata['ordernumber']
        
        
        
        # Dictionary containing the cart items
        cart = (
        {
        'quantity': 1,
        'reference': '123456789',
        'name': 'Klarna t-shirt',
        'unit_price': 12300,
        'discount_rate': 1000,
        'tax_rate': 2500
        }, {
        'quantity': 1,
        'type': 'shipping_fee',
        'reference': 'SHIPPING',
        'name': 'Shipping Fee',
        'unit_price': 4900,
        'tax_rate': 2500
        }
        )
                
        # Merchant ID
        eid = '2290'
        settings.klarna_eid
        
        # Shared Secret
        shared_secret = 'qzjaNjloMvifB6z'
        #settings.klarna_secret
        
        
        klarnacheckout.Order.base_uri = \
            'https://checkout.testdrive.klarna.com/checkout/orders'
        klarnacheckout.Order.content_type = \
            'application/vnd.klarna.checkout.aggregated-order-v2+json'
        
        connector = klarnacheckout.create_connector(shared_secret)
        
        order = None
        
        merchant = {
            'id': eid,
            'terms_uri': 'http://example.com/terms.html',
            'checkout_uri': 'http://example.com/checkout',
            'confirmation_uri': ('http://example.com/thank-you' +
                                 '?sid=123&klarna_order={checkout.order.uri}'),
        # You can not receive push notification on
        # a non publicly available uri
        #'push_uri': ('http://example.com/push' +
        #             '?sid=123&klarna_order={checkout.order.uri}')
        }
        
        import pdb; pdb.set_trace()
        
        data = {
                'purchase_country': 'SE',
                'purchase_currency': 'SEK',
                'locale': 'sv-se',
        'merchant': merchant
        }
        
        data["cart"] = {"items": []}
        
        for item in cart:
            data["cart"]["items"].append(item)
        
        order = klarnacheckout.Order(connector)
        order.create(data)

