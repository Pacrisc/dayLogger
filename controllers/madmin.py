# -*- coding: utf-8 -*-

if not auth.user:
    redirect(URL(c='default', f='user', args=['login']))

@auth.requires_membership('admin')
def users():
    db.auth_user.registration_key.readable=True
    grid = SQLFORM.grid(db.auth_user,
                   fields=[db.auth_user.id, db.auth_user.first_name,
                           db.auth_user.last_name, db.auth_user.registration_key, db.auth_user.email],
                   orderby = [~db.auth_user.id]
                   )
    return locals()

@auth.requires_membership('admin')
def impersonate():
    if request.vars.uid:
        uid = int(request.vars.uid)
        session.imp_user = db(db.auth_user.id == uid).select().first()
        if not session.imp_user:
            raise ValueError
        redirect(URL('default', 'index'))
    else:
        if session.imp_user:
            del session.imp_user
            redirect(URL('madmin', 'users'))

@auth.requires_membership('admin')
def tags():
    grid = SQLFORM.grid(db.tags)

    Ntags = db(db.tags).count()

    return dict(grid=grid, Ntags=Ntags)

@auth.requires_signature()
@auth.requires_membership('admin')
def prepopulate_tags():
# prepopulate tags table
    if not db(db.tags).count():
        with open('./applications/dayLogger/modules/nounlist.txt', 'r') as f:
            for line in f:
                db.tags.insert(name=line.strip())
        return 'window.location.reload();'
    else:
        return ''
