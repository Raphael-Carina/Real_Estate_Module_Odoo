from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = """Model used to create new type of properties, used un the estate.property model to create instance"""

    # ================
    # Champs du modèle
    # ================

    name = fields.Char(required=True)