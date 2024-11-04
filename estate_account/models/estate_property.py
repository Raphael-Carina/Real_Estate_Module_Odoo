from odoo import fields, models

class EstateProperty(models.Model):
    _inherit = 'estate.property'
    _description = """This model inherit from the estate.property model from the estate module.
    The main objective is to add specific comportment of the sold action to automaticaly create an invoice."""

    def action_sold(self):
        print('Méthode action_sold surchargée !')
        return super().action_sold()