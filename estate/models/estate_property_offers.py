from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError

class EstatePropertyOffers(models.Model):
    _name = "estate.property.offers"
    _description = """Model used to create offers for a given record of estate.property model."""
    _order = "price desc" # Les plus chères en haut

    # ===============
    # Contraintes SQL
    # ===============

    _sql_constraints = [
        ('check_positive_price','CHECK(price > 0)','The price of an offer shoud be strictly positive !')
    ]

    # ================
    # Champs du modèle
    # ================

    price = fields.Float()
    possible_status = [('accepted','Accepted'),('refused','Refused')]
    status = fields.Selection(selection=possible_status, copy=False)
    partner_id = fields.Many2one(comodel_name='res.partner', required=True)
    property_id = fields.Many2one(comodel_name='estate.property', required=True)
    create_date = fields.Date(default=fields.Date.today(), readonly=True)

    validity = fields.Integer(default=7, string="Validity (days)")
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    # Le champ suivant (property_type_id) permet de relier l'offre à un type de propriété.
    # L'offre prends le même type de propriété que le type de propriété qui est indiqué dans l'annonce (-> cad dans le modèle estate.property).
    property_type_id = fields.Many2one(comodel_name='estate.property.type', related='property_id.property_type_id', store=True) # Champ relatif !

    @api.depends("create_date","validity")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = fields.Date.add(record.create_date, days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - record.create_date).days


    """
    Explications sur les champs :
    _____________________________


    - partner_id. Les offres ont besoin d'être 'réalisées' par quelqu'un (=le client). Le champs partner_id représente justement le client qui émet l'offre.
      Un lien est fait avec le modèle 'res.partner'. Une offre ne peut avoir qu'un seul client mais un client peut faire plusieurs offres. On retrouve donc la
      notion de relation Many2one.

    - property_id. Une offre doit être liée à une annonce. Une offre ne peut avoir qu'une seul annonce correspondante mais une annonce peut avoir plusieurs offres.
      On retrouve donc là aussi le principe de relation Many2one. On fait donc le lien avec le modèle estate.property. C'est ce champ qui vas relier une offre à l'annonce en question.
    

    Les méthode _inverse :
    ______________________

    Précédemment, avec les champs calculés, on remarque qu'ils sont par défaut en readonly.
    En effet, l'utilisateur n'a pas à saisir sa valeur puisqu'il est calculé en fonction d'autre(s) champ(s).
    Dans certains cas, on aimerait quand même pouvoir les modifier.
    C'est le cas avec nos champs validity et date_deadline. En effet chacun de ces 2 champs à un impact sur l'autre et il faut bien pouvoir en saisir un pour définir l'autre.
    Cela est permit dans Odoo avec les méthodes _inverse.

    -> Une méthode _compute donne la valeur du champ tandis qu'une méthode _inverse donne la valeur du/des champ(s) mis en dépendances.

    Il est à noter qu'une méthode _inverse est appelée lors de l'enregistrement de l'enregistrement tandis qu'une méthode _compute est appelée à chaque modification d'une de ses dépendances.
    """

    # ===========
    # Les actions
    # ===========

    def action_accept_offer(self):
        """
        Action pour accepter une offre.
        On ne doit pas pouvoir accepter une offre déjà refuser.
        Lorsqu'une offre est acceptée, on doit définir les champs buyer et selling_price du modèle estate.property avec les valeurs de l'offre.
        Lorsqu'une offre est acceptée, on doit automatiquement refuser toutes les autres offres.
        """

        for record in self:
            if not record.status == 'refused':
                record.status = 'accepted'
                record.property_id.buyer = record.partner_id
                record.property_id.selling_price = record.price

                # Refuser les autres offres
                #__________________________

                # On cherche les autres offres : elles sont associées à la même annonce mais sont différentes de l'offre actuelle.
                other_offers = self.search([('property_id.id','=',self.property_id.id), ('id','!=',self.id)])

                # On mets à jour le state des autres offres sur 'refused'.
                other_offers.write({'status':'refused'})

            else:
                raise UserError("Refused offer can't be accepted !")
        
        return True

    def action_refuse_offer(self):
        """
        Action pour refuser une offre.
        On ne peut pas refuser une offre déjà acceptée.
        """

        for record in self:
            if not record.status == 'accepted':
                record.status = 'refused'
            else:
                raise UserError("Accepted offer can't be refused !")
            
        return True


    # ==========
    # L'héritage
    # ==========

    # Surcharge de la méthode create
    #_______________________________

    @api.model
    def create(self, vals):
        """
        vals est un dictionnaire qui contient les valeurs des champs saisis par l'utilisateur lors de la création d'une offre depuis l'interface utilisateur.
        """

        # On veut set le state de l'offre sur 'offer_received' quand une offre est créée ET ne pas pouvoir créer d'offre inférieur aux existantes
        print(vals)
        # On récupère la propriété liée à l'offre que l'on veut créer
        property = self.env['estate.property'].browse(vals['property_id'])
        print(property.name)
        # On récupère les offres liées à l'annonce
        existing_offers = property.offers_ids
        if existing_offers:
            highest_price = max(existing_offers.mapped('price'))
            if vals['price'] <= highest_price:
                raise ValidationError("Can't create offer with a lower price than existing offers !")
            
        # On crée l'offre
        offer = super().create(vals)
        offer.property_id.state = "offer_received"
        return offer