# Tips divers

### Se connecter en psql à la BDD

Le container postgres se nomme db, l'utilisateur postgres se nomme odoo (docker-compose.yml, POSTGRES_USER) et ma BDD realestate_tuto.

```bash
docker-compose exec db psql -U odoo -d realestate_tuto
```
