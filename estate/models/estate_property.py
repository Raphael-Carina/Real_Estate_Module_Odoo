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

    property_type_id = fields.Many2one(comodel_name='estate.property.type', string="Type")
    salesperson = fields.Many2one(comodel_name="res.users", default=lambda self: self.env.user)
    buyer = fields.Many2one(comodel_name="res.partner", copy=False)

    tags_ids = fields.Many2many(comodel_name='estate.property.tags')

    """
    Explications sur les différents fields et leurs attributs possibles :
    _____________________________________________________________________


    - l'attribut copy=False permet de faire en sorte que le champ en question ne soit pas copier/coller lorsque l'on duplique un enregistrement du modèle.
    - certains nom de champs sont réservés par Odoo. C'est le cas du nom 'active'. Lorsque ce champ est sur False, l'enregistrement en question disparait de la liste
    des enregistrements. Il faut modifier les filtres de recherche pour le retrouver.

    - les champs Many2one sont des liens vers d'autres objets. Ici on a le champ 'property_type_id' qui, à chaque création d'un enregistrement du modèle estate.property (=une annonce),
    pointe vers un enregistrement du modèle estate.property.type (=un type). Une annonce peut avoir qu'un seul type et un même type peut être utilisé dans plusieurs annonces.
    Ces champs se comportent comme une liste d'enregistrement de taille 0 ou 1 (recordset of 0 or 1 record).

    - les champs Many2many sont des relations multiples et bidirectionnelles. Ici, on a le champ 'tags_ids'. Une propriété peut avoir plusieurs tags et chaque tags
    peut être utilisés dans plusieurs annonces. Chaque enregistrement d'un des 2 modèles (estate.property et estate.property.tags) peut être reliés à plusieurs enregistrement de l'autre modèle.
    Par exemple, un annonce peut être liée à plusieurs tags différents ET, de la même façon, un tag peut être relié à plusieurs annonces différentes.
    Ces champs se comportent comme un liste d'enregistrement (recordset).


    """

