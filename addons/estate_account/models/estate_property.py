from odoo import Command, fields, models
import logging

_logger = logging.getLogger(__name__)

class EstateProperty(models.Model):
    """This model inherit from the estate.property model from the estate module. The main objective is to add specific comportment of the sold action to automaticaly create an invoice."""
    _inherit = 'estate.property'

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

    """
    !!!!!!!!!!!!!!!!
    check_access() :
    ________________

    Malgré le fait que l'on ait crée des règles sur les enregistrements qui ne permettent au Agent de voir uniquement leur annonces,
    que les Manager puissent tout voir, et que le reste des gens n'aient aucun droit sur estate.property, on est pas à l'abri des appels RPC
    (voir rubrique ci-dessous).

    Puisque l'on a ajouté des .sudo() dans la méthode action_sold(), n'importe qui pourrait appeler la méthode et générer des factures
    depuis un appel RPC.
    Pour éviter cela, il est nécessaire de rajouter des vérifications sur les droits dans les méthodes où on ajoute un .sudo() .

    La méthode check_access() existe depuis la V18 et regroupe les 2 anciennes méthodes : check_access_rights(operation) et check_access_rule.
    - 'operation' vaut 'create', 'write', 'read' ou 'unlink'.
    - si l'accès est refusé, la méthode lève une AccessError; sinon elle ne retourne rien.
    - sur un recordset vide, comme par exemple self.env['account.move'], seuls les droits du modèle sont vérifiés.
    - en sudo(), elle ne vérifie rien du tout. Il faut donc l'appeler avant le passage en .sudo() !

    NB :
    - il existe deux variantes :
        - has_access(operation) : renvoie un booléen.
        - _filtered_access(operation) : renvoie uniquement les enregistrements autorisés.

    - on peut vérifier l'appartenance d'un utilisateur à un groupe avec : self.env.user.has_group().
    """

    """
    !!!!!!!!!!!!
    Appels RPC :
    ____________

    Un utilisateur connecté à Odoo a un cookie de session, il peut donc très (trop?) facilement exécuter une requête RPC.
    Prenons un exemple très concret :

    J'ai crée un nouvel utilisateur : 'random'. Il n'a aucun droit ni sur le module real_estate, ni en facturation (compta).
    Visuellement, cet utilisateur n'a donc pas accès ni au module Real Estate, ni a Facturation.
    Pourtant, il peut simuler un clic sur le bouton SOLD d'un propriété via un appel RPC.
    Pour cela, il a juste à ouvrir le DOM, puis dans console, faire :

fetch('/web/dataset/call_kw/estate.property/action_sold', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    jsonrpc: '2.0', method: 'call',
    params: {
      model: 'estate.property',
      method: 'action_sold',
      args: [[42]],
      kwargs: {}
    }
  })
});

    Dans son appel, il indique le modèle estate.property, ainsi que la méthode action_sold, puis l'annonce d'ID 42.
    En faisant ça, la méthode est exéctuée!

    Bien sûr, ce n'est pas à la portée de n'importe qui, puis il faut connaitre le modèle, la méthode et l'ID, mais c'est faisable.

    Puisque l'on a précédemment ajouté des .sudo() dans notre méthode action_sold() pour permettre aux Agents de SOLD des annonces
    sans avoir de droits spécifiques en facturation, la méthode devient très dangereuse car avec cet appel RPC, n'importe qui
    pourrait générer une facture.

    La solution est de vérifier les droits de l'utilisateur qui appel la méthode.
    C'est ce qui est fait avec la ligne 'self.check_access('write')'.
    Grâce à ça, l'utilisateur malveillant peut toujours appeler la méthode mais la vérification des droits le bloque directement.

    NB :
    - les méthodes privées (celle commençant par un '_') ne sont pas appelables depuis un appel RPC.
      Si on essaie, on a le message : Private methods (such as 'estate.property._compute_best_price') cannot be called remotely.

    - ici on vu l'exemple d'un utilisateur connecté à Odoo, mais il serait également possible de le faire hors du navigateur
      en connaissant son login et son mot de passe (/xmlrpc/2/object, execute_kw).

    - dans les logs Odoo, il n'est pas possible de distinguer un appel RPC d'un appel "standard" car l'interface web elle-même
      utilise du RPC.
    """

    def action_sold(self):
        # print('Méthode action_sold surchargée !')

        # On vérifie que l'utilisateur ait le droit de modifier l'annonce (est-ce que l'utilisateur à le write possible sur self).
        # En effet, SOLD revient à modifier l'annonce (son 'state' change).
        self.check_access('write')

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