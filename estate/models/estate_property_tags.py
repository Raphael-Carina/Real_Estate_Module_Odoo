from odoo import models, fields

class EstatePropetyTags(models.Model):
    _name = "estate.property.tags"
    _description = """Model used to create tags of properties. These tags should be used in the creation of estate.property record"""

    # ================
    # Champs du modèle
    # ================

    name = fields.Char(required=True)