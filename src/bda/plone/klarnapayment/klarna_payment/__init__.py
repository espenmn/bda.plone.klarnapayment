# -*- coding: utf-8 -*-

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
from bda.plone.orders.common import OrderData

from bda.plone.shop.interfaces import IShopSettings

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from bda.plone.klarnapayment import IKlarnaPaymentSettings

from plone.app.uuid.utils import uuidToURL


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
        uses klarna checkout
        """
    
    def __call__(self, **kw):
        uid = self.request['uid']
        base_url = self.context.absolute_url()
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IKlarnaPaymentSettings)
        
        data = IPaymentData(self.context).data(uid)
        
        #amount = data['amount']
        #description = data['description']
        #ordernumber = data['ordernumber']
        
        import pdb; pdb.set_trace()
        order_data = OrderData(self.context, uid)
        
        currency = data['currency']
        
        # Merchant ID
        eid = settings.klarna_eid
        
        # Shared Secret
        shared_secret = settings.klarna_secret
        
        #Add the cart items
        #cart = (
        #    {
        #        'quantity': 1,
        #        'reference': '123456789',
        #       'name': 'Klarna t-shirt',
        #        'unit_price': 12300,
        #        'discount_rate': 1000,
        #        'tax_rate': 2500
        #   },
        #)
        
        
        cart = list()
        for booking in order_data.bookings:
            cart.append({
                        'quantity': int(booking.attrs['buyable_count']),
                        'reference': uuidToURL(booking.attrs['buyable_uid']),
                        'name': booking.attrs['title'],
                        'unit_price': int(booking.attrs.get('net', 0.0)*100),
                        'discount_rate': int((booking.attrs['discount_net'])*100),
                        'tax_rate': int(booking.attrs.get('vat', 0.0)*100),
        })
        
        create_data = {}
        create_data["cart"] = {"items": []}
        
        for item in cart:
            create_data["cart"]["items"].append(item)
        
        #Configure the checkout order
        
        import pdb; pdb.set_trace()
        create_data['purchase_country'] = 'NO'
        create_data['purchase_currency'] = currency
        create_data['locale'] = 'nb-no'
        
        create_data['shipping_address'] = {
        'email' : 'espen@medialog.no',
        'given_name' : 'Espen',
        'family_name' : 'Moe',
        'postal_code' : '5067',
        'phone' : '55555555',
        }
        #create_data['billing_address'] = { 'phone' : '55555555', }
        
        create_data['merchant'] = {
            'id': eid,
            'terms_uri': 'http://example.com/terms.html',
            'checkout_uri': 'http://example.com/checkout',
            'confirmation_uri': ('http://example.com/thank-you' +
                                 '?sid=123&klarna_order={checkout.order.uri}'),
                                 'push_uri': ('http://example.com/push' +
                                              '?sid=123&klarna_order={checkout.order.uri}')
        }
        
        
        # Create a checkout order
        
        klarnacheckout.Order.base_uri = \
            'https://checkout.testdrive.klarna.com/checkout/orders'
        klarnacheckout.Order.content_type = \
            'application/vnd.klarna.checkout.aggregated-order-v2+json'
        
        connector = klarnacheckout.create_connector(shared_secret)
        
        order = klarnacheckout.Order(connector)
        order.create(create_data)
        
        
        
        
        # Render the checkout snippet
        
        order.fetch()
        
        # Store location of checkout session
        #session["klarna_checkout"] = order.location
        
        # Display checkout
        return "<div>%s</div>" % (order["gui"]["snippet"])