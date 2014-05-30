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
        
        data = IPaymentData(self.context).data(uid)
        
        # OrderData(self.context, self.uid)
        
        amount = data['amount']
        currency = data['currency']
        description = data['description']
        ordernumber = data['ordernumber']
        
        # Merchant ID
        eid =   settings.klarna_eid
        
        # Shared Secret
        shared_secret =  settings.klarna_secret
        
        #Add the cart items 
        cart = (
        	{
            'quantity': 1,
            'reference': ordernumber,
            'name': 'BMH',
            'unit_price': amount,
            'tax_rate': 2500
        	} 
        )
                
        create_data = {}
        create_data["cart"] = {"items": []}

        for item in cart:
            create_data["cart"]["items"].append(item)
        
        #Configure the checkout order
        
        create_data['purchase_country'] = 'NO'
        create_data['purchase_currency'] = currency
        create_data['locale'] = 'nb-no'

        #create_data['billing_address'] = {
        #    'given_name': 'Testperson-no',
        #	'family_name' : 'Approved',
        #	'street_address' : 'Sæffleberggate 56',
        #	'postal_code' : '0563'
        #}
        
        create_data['merchant'] = {
            'id': eid,
            'terms_uri': 'http://www.bmh.no/nettbutikk/agb',
            'checkout_uri': 'http://bmh.no/checkout',
            'confirmation_uri': ('http://bmh.no/thank-you')
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