# Divers tips

### Lancer Odoo en mode shell depuis le conteneur Odoo

Mon conteneur Odoo (service) se nomme od, et ma base de données realestate_tuto :

```bash
docker-compose exec od odoo shell /etc/odoo/odoo.conf -d realestate_tuto --no-http
```
