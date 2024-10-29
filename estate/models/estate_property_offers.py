from odoo import models, fields

class EstatePropertyOffers(models.Model):
    _name = "estate.property.offers"
    _description = """Model used to create offers for a given record of estate.property model."""

    # ================
    # Champs du modèle
    # ================

    price = fields.Float()
    possible_status = [('accepted','Accepted'),('refused','Refused')]
    status = fields.Selection(selection=possible_status, copy=False)
    partner_id = fields.Many2one(comodel_name='res.partner', required=True)
    property_id = fields.Many2one(comodel_name='estate.property', required=True)



    """
    Explications sur les champs :
    _____________________________


    - partner_id. Les offres ont besoin d'être 'réalisées' par quelqu'un (=le client). Le champs partner_id représente justement le client qui émet l'offre.
      Un lien est fait avec le modèle 'res.partner'. Une offre ne peut avoir qu'un seul client mais un client peut faire plusieurs offres. On retrouve donc la
      notion de relation Many2one.

    - property_id. Une offre doit être liée à une annonce. Une offre ne peut avoir qu'une seul annonce correspondante mais une annonce peut avoir plusieurs offres.
      On retrouve donc là aussi le principe de relation Many2one. On fait donc le lien avec le modèle estate.property. C'est ce champ qui vas relier une offre à l'annonce en question.
    
    """