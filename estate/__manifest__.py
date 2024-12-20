{
    'name' : "Real Estate",
    'installable': True,
    'author': "d'Artagnan",
    'description': """This module is used to create/organize estate properties.""",
    'depends': ['base'],
    'data': [
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tags_views.xml',
        'views/estate_property_offers_views.xml',
        'views/estate_menus.xml',
        'views/res_users_views.xml',

        'security/ir.model.access.csv',
        ]
}
