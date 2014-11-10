#!/usr/bin/python
# -*- coding: utf-8 -*-

if not auth.user:
    redirect(URL(c='default', f='user', args=['login']))


@auth.requires_signature()
def tags():
    if not request.vars.table or not request.vars.table in ['tag_events', 'tag_event_items']:
        raise HTTP(403)
    if not request.vars.parent_id or not request.vars.parent_id.isdigit():
        raise HTTP(403)
    table = str(request.vars.table)
    parent_id = int(request.vars.parent_id)
    if request.vars.readonly is not None:
        readonly = True
    else:
        readonly = False
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
        raise HTTP(403)

    table = str(request.vars.table)
    parent_id = int(request.vars.parent_id)
    action = request.args[0]
    tag_id = int(request.vars.tag_id)
    if table == 'tag_event_items':
        if action == 'add':
            res = db[table].insert(parent=parent_id, tag=tag_id)
        elif action == 'delete':
            q = (db[table].parent==parent_id)
            q &= (db[table].tag==tag_id)
            res = db(q).delete()
    else:
        record = db.events(parent_id)
        if not record:
            raise HTTP(403)
        id_list = db(db.events.parent_id==record.parent_id).select(db.events.id).as_dict().keys()
        if action == 'add':
            res = db[table].bulk_insert([{'parent': idx, 'tag': tag_id} for idx in id_list])
        elif action == 'delete':
            q = (db[table].parent.belongs(id_list))
            q &= (db[table].tag==tag_id)
            res = db(q).delete()

    return res

def jeditable():
    """ This is not secure """
    import re
    import string
    if request.vars.id:
        _, field, mid = request.vars.id.split('_')
        mid = int(mid)

    sanitize_int = lambda x: float(re.sub('[^0-9+\-.eE]+', '', x))
    if field in ['description', 'value']:
        if has_item_permission(db.event_items[mid].parent):
            table = 'event_items'
            sanitize = {'description': string.strip, 'value': sanitize_int }[field]
        else:
            raise HTTP(403)

    elif field == 'registrationkey':
        if not auth.has_membership('auth'):
            field = 'registration_key' # renaming field in accordance with the db
            table = 'auth_user'
            sanitize = str
        else:
            raise HTTP(403)
    else:
        raise HTTP(403)

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
        rows  = db(db.tags.name.contains(q)).select()
        if rows:
            for row in rows:
                out.append({'id': row.id, 'name': row.name})
    return dict(data=out)


