#!/usr/bin/python
# -*- coding: utf-8 -*-

if not auth.user:
    redirect(URL(c='default', f='user', args=['login']))

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
            redirect(URL('default', 'user_admin'))

@auth.requires_signature()
def tags():
    if not request.vars.table or not request.vars.table in ['tag_events', 'tag_event_items']:
        raise ValueError
    if not request.vars.parent_id or not request.vars.parent_id.isdigit():
        raise ValueError
    table = str(request.vars.table)
    parent_id = int(request.vars.parent_id)
    form_name = '-'.join([request.vars.table, str(parent_id)])
    q = db[table].parent == parent_id
    q &= db[table].tag == db.tags.id
    prepopulate_tags = db(q).select(db.tags.ALL).as_list()
    return locals()

def manage_tags():
    if (not request.vars.table or not request.vars.table in ['tag_events', 'tag_event_items']) or \
       (not request.vars.parent_id or not request.vars.parent_id.isdigit()) or \
       (not request.vars.tag_id or not request.vars.tag_id.isdigit()) or \
       (not request.args or request.args[0] not in ['add', 'delete']):
        raise ValueError
    table = str(request.vars.table)
    parent_id = int(request.vars.parent_id)
    action = request.args[0]
    tag_id = int(request.vars.tag_id)
    if action == 'add':
        res = db[table].insert(parent=parent_id, tag=tag_id)
    elif action == 'delete':
        q = (db[table].parent==parent_id)
        q &= (db[table].tag==tag_id)
        res = db(q).delete()
    return res

def jeditable():
    """ This is not secure """
    import re
    if request.vars.id:
        _, field, mid = request.vars.id.split('_')
    sanitize_int = lambda x: int(re.sub('[^0-9+\-]+', '', x))
    if field in ['description', 'value']:
        table = 'event_items'
        sanitize = {'description': str, 'value': sanitize_int }[field]
    elif field == 'registrationkey':
        if not auth.has_membership('auth'):
            field = 'registration_key' # renaming field in accordance with the db
            table = 'auth_user'
            sanitize = str
        else:
            raise ValueError('Not allowed!')
    else:
        raise ValueError
        
    value = sanitize(request.vars.value) 
    if value or (not value and not request.vars.value):
        res = db(db[table].id==mid).update(**{field: value})
        if res:
            return value
        else:
            return value + '(no update)'
    else:
        return request.vars.value + '(error)'

def autocomplete_tags():
    import re
    out = []
    if request.vars.q and request.vars.parent_id:
        q = re.sub('\W+', '', request.vars.q).lower()
        #db_q = db.tags.name.contains(q)
        rows  = db(db.tags.name.contains(q)).select()
        if rows:
            for row in rows:
                out.append({'id': row.id, 'name': row.name})
        #else:
        #    # new tag in database, nothing matched, look into an external dict
        #    tag_list = ['sleep', 'food', 'work']
        #    for idx, tag_name in enumerate(tag_list):
        #        if q in tag_name:
        #            out.append({'id': -idx, 'name': tag_name})
    return dict(data=out)
