from odoo import Command, fields, models

class EstateProperty(models.Model):
    _inherit = 'estate.property'
    _description = """This model inherit from the estate.property model from the estate module.
    The main objective is to add specific comportment of the sold action to automaticaly create an invoice."""

    """
    sudo() :
    ________

    Nous avons crée un utilisateur "Real Estate Agent" (res.users), appartenant au groupe "Agent" (estate.estate_group_user).
    L'objectif est de faire en sorte que cet utilisateur puisse cliquer sur 'SOLD' sur une annonce, sans pour autant avoir les
    droits en facturation (comptabilité).
    Or, appuyer sur 'SOLD' trigger action_sold ci-dessous et génère une facture.

    Voici les possibilités :
    - Dans Utilisateurs / <utilisateur Real Estate Agent> / Droits d'accès, dans la rubrique "Facturation" (Invoicing), on peut
    lui mettre le groupe 'Basique' dans le champ 'Comptabilité'. Mais comme dis plus haut, le but et de ne pas lui donner d'accès
    à la compta du tout (c'est le but de l'exercice).

    - On peut (et on va) utiliser la méthode .sudo(), qui permet de créer un enregistrement sans tenir compte des droits d'accès (res.groups)
    ni des règles sur les enregistrements (ir.rule).

    - Une autre possibilité serait de carrément exécuter une requête SQL brute. Cela a carrément pour effet de bypasser l'ORM Odoo.

    D'une façon générale, l'utilisation de .sudo() et des requêtes SQL sont a utiliser uniquement dans des cas très précis, où le besoin
    est nécessaire et clairement identifié. Une bonne pratique est d'éviter un maximum de créer des enregistrements à partir de champs remplis
    par l'utilisateur avec .sudo() (car il peut insérer des conneries concrètement). Dans notre exemple de génération automatique de facture
    ci-dessous, l'utilisateur ne complète rien, elle se génère automatiquement avec les infos renseignées dans la méthode action_sold(), donc
    l'impact du .sudo() est limité.

    NB : On utilise .sudo() pour la création de la facture (account.move) mais aussi pour la recherche du journal dans 'journal_id'.
    """

    def action_sold(self):
        # print('Méthode action_sold surchargée !')

        # On souhaite générer une facture automatique lorsqu'une annonce est vendue (c'est à dire lorsque l'action action_sold est trigger)
        invoice = self.env['account.move'].sudo().create({
            'partner_id' : self.buyer.id,
            'move_type': 'out_invoice',
            'journal_id': self.env['account.journal'].sudo().search([('type', '=', 'sale')], limit=1).id,

            # Création de ligne de facture (invoice lines)
            'invoice_line_ids' : [
                Command.create({
                    "name": "6% Selling Price",
                    "quantity": 1,
                    "price_unit": self.selling_price * 0.06,
                }),
                Command.create({
                    "name": "Administrative fees",
                    "quantity": 1,
                    "price_unit": 100
                }),
            ],
        })

        return super().action_sold()