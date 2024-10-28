{
    'name' : "Real Estate",
    'installable': True,
    'author': "d'Artagnan",
    'description': """This module is used to create/organize estate properties.""",
    'depends': ['base'],
    'data': [
        'views/estate_property_views.xml',

        'security/ir.model.access.csv',
        ]
}
