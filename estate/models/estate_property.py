import sys

sys.path.append('C:\\Users\\Raphaël\\dev\\odoo17\\odoo')

from odoo import api, models, fields
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = """This model is used to create real estate properties ads"""

    # ===============
    # Contraintes SQL
    # ===============

    _sql_constraints = [
        ('check_positive_expected_price','CHECK(expected_price > 0)','The expected price should be strictly positive !'),
        ('check_positive_selling_price', 'CHECK(selling_price > 0)','The selling price should be strictly positive !')
    ]

    # ==============
    # Model's fields
    # ==============

    # Champs basiques
    #________________

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

    # Champs relationnels
    #____________________

    property_type_id = fields.Many2one(comodel_name='estate.property.type', string="Type")
    salesperson = fields.Many2one(comodel_name="res.users", default=lambda self: self.env.user)
    buyer = fields.Many2one(comodel_name="res.partner", copy=False)

    tags_ids = fields.Many2many(comodel_name='estate.property.tags')

    offers_ids = fields.One2many(comodel_name='estate.property.offers', inverse_name='property_id', string="Offers")

    """
    Explications sur les différents fields et leurs attributs possibles :
    _____________________________________________________________________


    - l'attribut copy=False permet de faire en sorte que le champ en question ne soit pas copier/coller lorsque l'on duplique un enregistrement du modèle.
    - certains nom de champs sont réservés par Odoo. C'est le cas du nom 'active'. Lorsque ce champ est sur False, l'enregistrement en question disparait de la liste
    des enregistrements. Il faut modifier les filtres de recherche pour le retrouver.

    - les champs Many2one sont des liens vers d'autres objets. Ici on a le champ 'property_type_id' qui, à chaque création d'un enregistrement du modèle estate.property (=une annonce),
    pointe vers un enregistrement du modèle estate.property.type (=un type). Une annonce peut avoir qu'un seul type et un même type peut être utilisé dans plusieurs annonces.
    Ces champs se comportent comme une liste d'enregistrement de taille 0 ou 1 (recordset of 0 or 1 record).
    On peut imaginer les champs Many2one comme des menus déroulants dans un formulaire.

    - les champs Many2many sont des relations multiples et bidirectionnelles. Ici, on a le champ 'tags_ids'. Une propriété peut avoir plusieurs tags et chaque tags
    peut être utilisés dans plusieurs annonces. Chaque enregistrement d'un des 2 modèles (estate.property et estate.property.tags) peut être reliés à plusieurs enregistrement de l'autre modèle.
    Par exemple, un annonce peut être liée à plusieurs tags différents ET, de la même façon, un tag peut être relié à plusieurs annonces différentes.
    Ces champs se comportent comme un liste d'enregistrement (recordset).

    - les champs One2many. Ici on a le champ offers_ids. Il s'agit de la même relation qu'une relation Many2one mais vue depuis l'autre modèle.
    Pour l'exemple des offres :
        - dans le modèle estate.property.offers : une offre ne correspond qu'à une seule annonce mais une annonce peut avoir plusieurs offres.
          Il y a donc une relation Many2one entre les deux modèles DU POINT DE VUE du modèle estate.property.offers, symbolisée par le champ property_id.

        - dans le modèle estate.property : une annonce peut avoir plusieurs offres mais une offre n'est reliée qu'à une seule annonce. --> ça revient au même
          qu'une relation Many2one mais inversée. Pour avoir accès aux offres d'une annonce, on passe donc par une relation One2many (le champ offers_ids), qui
          inverse le champ property_id du modèle estate.property.offers.
    
    Ces champs se comportent comme un liste d'enregistrement (recordset).
    Attention : les relations One2many sont dites 'virtuelles'. Pour exister, il est nécessaire qu'il y ait un champ Many2one dans le modèle lié.
    """

    # Champs calculés
    #________________

    total_area = fields.Float(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    @api.depends("living_area","garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offers_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offers_ids.mapped('price'), default=0.0) # Nécessaire de mettre 0 par défaut dans le cas où il n'y a pas d'offres pour l'annonce

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = False
            self.garden_orientation = False


    """

    Explications sur les champs calculés :
    ______________________________________

    
    Jusqu'à présent, avec les champs basiques, leurs valeurs étaient directement stockées puis extraites de la base de données.
    Avec les champs calculés comme notre champ total_area, c'est différent. Sa valeur n'est pas directement stockée dans la bdd. Sa valeur est calculée à la volée
    via la méthode _compute_total_area (On peut stocker les valeurs des champs calculer avec store=True mais ça peut être dangereux car ces champs seraient recalculés pour tous les enregistrements chaque fois qu'un dépendance changerait).

    Une méthode _compute doit calculer le champ calculé pour tous les enregistrement du modèle ! C'est pour ça qu'on doit nécessairement boucler sur le self.

    Par convention, les méthodes _compute sont toujours privées (d'où le underscore).

    best_price. -> il est possible d'utiliser les chemins vers un champ dans un modèle lié via un champ relationnel comme dépendance.
                    Dans notre cas, on dit que la valeur du champ best_price dépend du champ price dans le modèle estate.property.offers via le champ offers_ids (One2many).
                    Cela fonctionne avec tous les types de champs relationnels : Many2one, Many2many, One2many.
                    Il est nécessaire de placer une valeur par défaut (ici sur 0), sinon max() retourne une 'empty sequence' et on ne peut plus ni ouvrir des annonces sans offre ni créer de nouvelles annonces (car le champ best_price ne trouve pas de valeur).

                    
    Les méthode _inverse : (dans estate.property.offers)
    ______________________

    Précédemment, avec les champs calculés, on remarque qu'ils sont par défaut en readonly.
    En effet, l'utilisateur n'a pas à saisir sa valeur puisqu'il est calculé en fonction d'autre(s) champ(s).
    Dans certains cas, on aimerait quand même pouvoir les modifier.
    C'est le cas avec nos champs validity et date_deadline. En effet chacun de ces 2 champs à un impact sur l'autre et il faut bien pouvoir en saisir un pour définir l'autre.
    Cela est permit dans Odoo avec les méthodes _inverse.

    -> Une méthode _compute donne la valeur du champ tandis qu'une méthode _inverse donne la valeur du/des champ(s) mis en dépendances.

    Il est à noter qu'une méthode _inverse est appelée lors de l'enregistrement de l'enregistrement tandis qu'une méthode _compute est appelée à chaque modification d'une de ses dépendances.


    Les onchange :
    ______________

    Les onchange ne s'appliquent que dans les form. self représente alors l'enregistrement dans le form.
    Lorsqu'un champ indiqué dans le décorateur onchange() est modifié, la méthode _onchange est trigger.

    -> les _compute et les _onchange permettent souvent d'arriver au même résultat.
    Il est préférable d'utiliser les _compute car ils sont activés dans des contextes hors des vues form.

    """

    # ===========
    # Les actions
    # ===========

    def action_sold(self):
        """
        Quand cette action est trigger via le bouton, on veut passer le state de l'annonce sur sold.
        On ne veut pas pouvoir trigger cette action si le state de l'annonce est déjà cancelled.
        """

        for record in self:
            if not record.state == "cancelled":
                record.state = 'sold'
            else:
                raise UserError("Cancelled property can't be sold !")

            return True
    
    def action_cancelled(self):
        """
        Quand cette action est trigger via le bouton, on veut passer le state de l'annonce sur canceled.
        On ne veut pas pouvoir trigger cette action si le state de l'annonce est déjà sur sold.
        """

        for record in self:
            if not record.state == 'sold':
                record.state = 'cancelled'
            else:
                raise UserError("Sold property can't be cancelled !")

            return True
        
    """

    Les actions :
    _____________

    Les actions ne sont pas des méthodes privées, on ne mets donc pas le underscore devant leurs noms.
    Cela les rends 'callable' depuis un call RPC.

    On boucle également sur le self car la méthode doit pouvoir être appelée sur plusieurs enregistrements (même tous).

    Une méthode publique doit toujours retourner quelque chose, c'est pour ça qu'on fait au moins un return True.
    """