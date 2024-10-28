import sys

sys.path.append('C:\\Users\\Raphaël\\dev\\odoo17\\odoo')

from odoo import models, fields



class EstateProperty(models.Model):
    _name = "estate.property"
    _description = """This model is used to create real estate properties ads"""

    # ==============
    # Model's fields
    # ==============

    name = fields.Char(string='Title', required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=fields.Date.add(fields.Date.today(), months=3))
    date_available_from = fields.Date(copy=False, string="Available From", default=fields.Date.today(), readonly=True)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(selection=[('south','South'),('west','West'),('north','North'),('east','East')])
    active = fields.Boolean(default=True)
    possible_state = [('new','New'),('offer_received','Offer Received'),('offer_acceptred','Offer Accepted'),('sold','Sold'),('cancelled','Cancelled')]
    state = fields.Selection(selection=possible_state, required=True, copy=False, default='new')

    """
    Explications sur les différents fields et leurs attributs possibles :
    _____________________________________________________________________


    - l'attribut copy=False permet de faire en sorte que le champ en question ne soit pas copier/coller lorsque l'on duplique un enregistrement du modèle.
    - certains nom de champs sont réservés par Odoo. C'est le cas du nom 'active'. Lorsque ce champ est sur False, l'enregistrement en question disparait de la liste
    des enregistrements. Il faut modifier les filtres de recherche pour le retrouver.
    """

