from odoo import models, fields

class EstatePropertyTags(models.Model):
    """Model used to create tags of properties. These tags should be used in the creation of estate.property record"""
    _name = "estate.property.tags"
    _description = "Estate Property Tags"
    _order = "name"

    # ===============
    # Contraintes SQL
    # ===============

    _sql_constraints = [
        ('check_unique_tags','UNIQUE(name)','A property tag should be unique !')
    ]

    # ================
    # Champs du modèle
    # ================

    name = fields.Char(required=True)
    color = fields.Integer()