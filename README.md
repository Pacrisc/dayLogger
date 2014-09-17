dayLogger
=========

A simple web2py day logger to track your daily biologically relevant events


To approve registration of the admin

```bash
$ python web2py.py -S dayLogger -M
```

```python
db(db.auth_user.email=='some_email').update(registration_key='')
db.auth_group.insert(role='admin')
db.auth_membership.insert(user_id=1, group_id=2)
db.commit()
```


    
