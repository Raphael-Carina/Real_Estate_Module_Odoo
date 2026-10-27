# Divers tips

### Lancer Odoo en mode shell depuis le conteneur Odoo

Mon conteneur Odoo (service) se nomme od, et ma base de données realestate_tuto :

```bash
docker-compose exec od odoo shell /etc/odoo/odoo.conf -d realestate_tuto --no-http
```

### Se connecter en psql à la BDD

Le container postgres se nomme db, l'utilisateur postgres se nomme odoo (docker-compose.yml, POSTGRES_USER) et ma BDD realestate_tuto.

```bash
docker-compose exec db psql -U odoo -d realestate_tuto
```

### Connaitre la date du dernier commit du dépôt enterprise

```bash
git -C enterprise log -1 --format=%cd
```

### Lister les différentes images Odoo 18.0 disponibles sur Docker Hub

```bash
curl -s "https://hub.docker.com/v2/repositories/library/odoo/tags?page_size=100&name=18.0-" \
  | jq -r '.results[].name' | sort
```

Sinon, on peut directement aller sur le site Docker Hub.

On peut ensuite mettre à jour notre fichier docker-compose.yml pour spécifier le tag de la version Odoo 18.0 que l'on veut.
C'est ce que j'ai fais en indiquant :

```yml
services:
  od:
    image: odoo:18.0-20261015
```

Ensuite, on fait :

```bash
docker compose pull
docker compose up -d --force-recreate
```

La première commande récupère l'image 18.0-20261015 depuis le docker hub et l'installe en local sur ma machine.
La seconde recréer le container odoo en l'obligeant à prendre en compte la nouvelle version du fichier docker-compose.yml .

Ensuite, on peut vérifier la version d'Odoo du container od :

```bash
docker-compose exec od dpkg -l odoo
````

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
