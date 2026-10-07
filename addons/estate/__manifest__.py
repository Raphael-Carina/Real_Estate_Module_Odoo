{
    'name' : "Real Estate",
    'installable': True,
    'author': "d'Artagnan",
    'description': """This module is used to create/organize estate properties.""",
    'depends': ['base'],
    'data': [
        'views/estate_property_views.xml',
        'views/estate_property_tags_views.xml',
        'views/estate_property_offers_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_menus.xml',
        'views/res_users_views.xml',

        # DATAS
        # Données de base du modèle estate.property.type (directement à l'installation du module).
        'data/estate.property.type.csv',

        # Données de base du modèle estate.property
        'data/estate_property_data.xml',

        # Données de base pour le modèle estate.property.offers
        'data/estate_property_offers_data.xml',

        'security/ir.model.access.csv',
        ]
}
