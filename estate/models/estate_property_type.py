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

    name = fields.Char(required=True)