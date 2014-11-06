# -*- coding: utf-8 -*-

# redirect to the login page by default
if not auth.user and request.function != 'user':
    redirect(URL(c='default', f='user', args=['login']))

def index():
    """
    """
    count_op = db.events.id.count()
    q = db.events.id>0
    if not is_admin:
        q &= db.events.created_by == auth.user_id
    elif session.imp_user:
        q &= db.events.created_by == session.imp_user.id

    rows = db(q).select(db.events.ALL, count_op,
                        groupby=db.events.edate)
    return dict(rows=rows, count_op=count_op)


def all_days():
    count_op = db.events.id.count()
    q = db.events.id>0
    if not is_admin:
        q &= db.events.created_by == auth.user_id
    elif session.imp_user:
        q &= db.events.created_by == session.imp_user.id

    rows = db(q).select(db.events.ALL, count_op,
                        groupby=db.events.edate)
    return dict(rows=rows, count_op=count_op)


def day():
    """
    """
    if request.args:
        q = db.events.edate==str2date(request.args(0))
        
        if not auth.has_membership('admin'):
            q &= db.events.created_by == auth.user_id
        elif session.imp_user:
            q &= db.events.created_by == session.imp_user.id
        rows = db(q).select(orderby=db.events.etime)
        #session.flash = str(str2date(request.args(0)))
        
        return dict(rows=rows)

    #session.flash = 'Wrong arguments for the day page!'
    redirect(URL(c='default', f='index'))


def top_events():
    q = db.events.id>0
    if not auth.has_membership('admin'):
        q &= db.events.created_by == auth.user_id
    elif session.imp_user:
        q &= db.events.created_by == session.imp_user.id

    count = db.events.id.count()
    rows = db(q).select(db.events.ALL, count, orderby=db.events.id, groupby=db.events.parent_id)
    return dict(rows=rows, weight = [el[count] for el in rows])



@auth.requires_signature()
def form_wrapper():
    mvars = {key: val for key, val in request.vars.iteritems()}
    margs = []
    table = None
    for idx, val in enumerate(request.args):
        if idx == 0:
            table = val
        else:
            margs.append(val)
    if table == 'event':
        murl = {'c': 'default', 'f': 'events'}
    elif table == 'eventitem':
        murl = {'c': 'default', 'f': 'event_item_handler'}
    else:
        murl = {}
    return LOAD(ajax_trap=True, user_signature=True, args=margs, vars=mvars, **murl)


#@auth.requires_signature()
def event_item_handler():
    """ Create new events """
    if request.args:
        mid = int(request.args[0])
        if not has_item_permission(db.events[mid]):
            raise HTTP(403)

    db.event_items.parent.default = mid
    form = SQLFORM(db.event_items, formstyle='bootstrap')
    if form.process().accepted:
        session.flash = 'Event item submitted!'
        # bulk insert event_items for all events in the group
        record = db.events[mid]
        q = (db.events.parent_id==record.parent_id) & (db.events.id != mid)
        event_ids =  db(q).select(db.events.id).as_dict().keys()
        db.event_items.bulk_insert([{'parent': eid, 'description': form.vars.description} for eid in event_ids])
        # just reload the whole page 
        redirect(URL(c='default', f='events', args=[mid], vars={'a': 'show'},
                                            user_signature=True), client_side=True)
    elif form.errors:
        response.flash = 'Errors in event form!'
    return dict(form=form)


def events():
    d = None
    form = None
    rows = []
    vargs = {}
    action = request.vars.a
    if request.args:
        mid = int(request.args[0])
        if action in ['delete', 'update', 'clone']:
            if not has_item_permission(db.events(mid)):
                raise HTTP(403)
    else:
        mid = None
    if action == 'delete':
        if mid:
            q = (db.events.parent_id == mid) & (db.events.id != mid)
            children = db(q).select(db.events.id, orderby=db.events.id).first()
            # make sure than when an event is deleted, it's children
            # are transferred to the another event in the same group
            if children:
                alternative_id = children.first().id
                db(q).update(parent_id == alternative_id)
            res = db(db.events.id == mid).delete()
            if res:
                redirect(URL('default', 'index'), client_side=True)

    elif action in ['update', 'create']:
        if mid:
            record = db.events(mid)
        else:
            record = None
        if request.vars.day_date and not mid:
            db.events.edate.default = str2date(request.vars.day_date)
        form = SQLFORM(db.events, record, formstyle='bootstrap')
        if form.process().accepted:
            #session.flash = 'Event submitted!'
            if not mid:
                db(db.events.id==form.vars.id).update(parent_id=form.vars.id)
            else:
                record = db.events[mid]
                db(db.events.parent_id==record.parent_id).update(title=form.vars.title,
                                                description=form.vars.description)

            redirect(URL(c='default', f='events', args=[form.vars.id],
                            vars={'a': 'show'}, user_signature=True))
        elif form.errors:
            response.flash = 'Errors in event form!'
    elif action == 'clone':
        record = db.events(mid)
        # assume that the tree has maximum depth of 1
        if record.parent_id != record.id:
            mid = record.parent_id
            record = db.events(mid)
        parent_id = mid
        if not record:
            raise HTTP(503, 'Wrong arguments!')
        today = datetime.datetime.today()
        event_id = db.events.insert(title=record['title'],
                                description=record['description'],
                                edate=today.date(),
                                etime=today.time(), 
                                parent_id=parent_id)
        tags_id_list = [el['tag'] for el in  db(db.tag_events.parent==parent_id).select(db.tag_events.tag)]
        for tag_id in tags_id_list:
            db.tag_events.insert(parent=event_id, tag=tag_id)
        for event_item in  db(db.event_items.parent==parent_id).select():
            event_item_id = db.event_items.insert(parent=event_id, 
                                                  description=event_item.description)
            tags_id_list = [el['tag'] for el in  db(db.tag_event_items.parent==parent_id).select(db.tag_event_items.tag)]
            for tag_idx in tags_id_list:
                db.tag_event_items.insert(parent=event_item_id, tag=tag_idx)
        redirect(URL(c='default', f='events', args=[event_id],
                            vars={'a': 'show'}, user_signature=True))

    elif action == 'show':
        mid = int(request.args[0])
        record = db.events(mid)
        count = db.events.id.count()
        begin_date = db.events.edate.min()
        end_date = db.events.edate.max()
        rows_group =  db(db.events.parent_id==record.parent_id).select(count, begin_date, end_date).first()
        vargs['count'] = rows_group[count]
        vargs['begin_date'] = rows_group[begin_date]
        vargs['end_date'] = rows_group[end_date]
        if record is None:
            response.flash = 'Something went wrong!'
        rows = db(db.event_items.parent==record.id).select()
    else:
        raise HTTP(403)

    return dict(record=record, form=form, action=action, rows=rows, vargs=vargs)


@auth.requires_signature()
def delete_event_item():
    mid = int(request.args[0])
    record = db.event_items[mid]
    event = db.events[record.parent]
    if has_item_permission(record.parent):
        event_id_list = db(db.events.parent_id == event.parent_id).select(db.events.id).as_dict().keys()
        q = db.event_items.parent.belongs(event_id_list)
        q &= db.event_items.description == record.description
        db(q).delete()
        return "$('tr#event_item_{0}').remove();".format(mid)
    else:
        raise HTTP(403)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)



