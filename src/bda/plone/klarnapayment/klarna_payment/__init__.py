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

#from ZTUtils import make_query

_ = MessageFactory('bda.plone.klarnapayment')
logger = logging.getLogger('bda.plone.payment')

CREATE_PAY_INIT_URL = "https://checkout.testdrive.klarna.com/checkout/orders"

class Klarna(Payment):
    pid = 'klarna'
    label = _('klarna', 'Klarna')
    available = True
    default = True
    
    def init_url(self, uid):
        return '%s/@@klarna?uid=%s' % (self.context.absolute_url(), uid)


class DoKlarna(BrowserView):
    """ Assembles an url to klarna.
        Maybe I should check how to use
        make_query()
        """
    def __call__(self, **kw):
        order_uid = self.request['uid']
        uid = self.request['uid']
        
        klarna_url = CREATE_PAY_INIT_URL
        
        data = IPaymentData(self.context).data(order_uid)
        
        amount = data['amount']
        currency = data['currency']
        description = data['description']
        ordernumber = data['ordernumber']
        
        parameters = {
            'amount':           amount,
            'currency':         currency,
            'merchant':         4255617,
            'language':         "nb_NO",
            'acceptReturnUrl':  self.context.absolute_url() + '/klarnaed?uid=' + order_uid,
            'cancelreturnurl':  self.context.absolute_url() + '/klarna_payment_aborted',
            'orderId':          ordernumber,
        }
        
        
        #assembles final url
        param = []
        for k, v in parameters.items():
            param.append("%s=%s" % (k, v))
        
        param = "&".join(param)
        
        self.request.response.redirect("%s?%s" % (klarna_url, param))



class KlarnaFinished(BrowserView):
    
    def id(self):
        uid = self.request.get('uid', None)
        payment = Payments(self.context).get('klarna')
        payment.succeed(self.request, uid)
        
        try:
            order = get_order(self.context, uid)
        except ValueError:
            return None
        return order.attrs.get('ordernumber')