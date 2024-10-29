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
        'views/estate_menus.xml',

        'security/ir.model.access.csv',
        ]
}
