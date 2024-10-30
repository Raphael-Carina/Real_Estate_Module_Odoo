from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = """Model used to create new type of properties, used un the estate.property model to create instance"""

    # ===============
    # Contraintes SQL
    # ===============
    
    _sql_constraints = [
        ('check_unique_type','UNIQUE(name)','A property type should be unique !')
    ]


    # ================
    # Champs du modèle
    # ================

    # Champs basiques
    #________________

    name = fields.Char(required=True)

    # Champs relationels
    #___________________

    property_ids = fields.One2many(comodel_name='estate.property', inverse_name='property_type_id')