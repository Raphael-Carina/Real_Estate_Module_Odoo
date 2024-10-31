from odoo import api, models, fields

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = """Model used to create new type of properties, used un the estate.property model to create instance"""
    _order = "sequence, name"

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
    sequence = fields.Integer(string="Sequence", default=1, help="Used to order type.") # Champ utilisé pour gérer l'order manuel dans la tree view du modèle

    # Champs relationels
    #___________________

    property_ids = fields.One2many(comodel_name='estate.property', inverse_name='property_type_id')
    offers_ids = fields.One2many(comodel_name='estate.property.offers', inverse_name='property_type_id')

    # Champs calculés
    #________________

    offer_count = fields.Integer(compute="_compute_offer_count")

    @api.constrains("offers_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offers_ids)
