from bda.plone.shop import message_factory as _

from zope import schema
from plone.supermodel import model
from zope.interface import Interface
from zope.interface import Attribute
from zope.interface import provider

from bda.plone.shop.interfaces import IShopSettingsProvider

@provider(IShopSettingsProvider)
class IKlarnaPaymentSettings(model.Schema):
    
    model.fieldset( 'klarna',label=_(u'Klarna', default=u'Klarna'),
        fields=[
        'klarna_eid',
        'klarna_secret',
        ],
    )
                   
    klarna_eid = schema.TextLine(title=_(u'eid', default=u'Eid'),
                 required=True
    )

    klarna_secret = schema.TextLine(title=_(u'secret', default=u'Shared Secret'),
               required=True
    )