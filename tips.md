# Tips divers

## Recharger la vue des droits d'accès des utilisateurs

Si la page est mal chargée (affichage bizzare) :

```bash
docker-compose exec od odoo shell -c /etc/odoo/odoo.conf -d real_estate --no-http
```

Puis dans le mode shell :

```python
env['res.groups']._update_user_groups_view()
env.cr.commit()
exit()
```
