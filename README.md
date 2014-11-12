dayLogger
=========

A simple web2py day logger to track your daily biologically relevant events



Dependencies
------------
 
 This application requres `python-2.7`, `pandas` and an active internet conexion (some js libraries are loaded from a CDN).

Installation notes
------------------

```bash
$ wget http://www.web2py.com/examples/static/web2py_src.zip
$ unzip web2py_src.zip
$ cd web2py/applications/
$ git clone git@github.com:Pacrisc/dayLogger.git
$ cd ../
```
By default, a sqlite database is used for storage. This can be changed by editing `applications/dayLogger/models/000_private.py`.

The app can be started locally at http://127.0.0.1:8000/dayLogger/ with
```bash
$ python web2py.py --nogui
```

The first registred user can be granted admin rights on the app from the command line
```bash
$ python web2py.py -S dayLogger -M
```

```python
db(db.auth_user.email=='your_email').update(registration_key='')
db.auth_group.insert(role='admin')
db.auth_membership.insert(user_id=1, group_id=2)
db.commit()
```


Upgrade notes
-------------
 Please read the [release_notes.md](./release_notes.md)

    
