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


def events():
    """
    """
    return dict()

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
        murl = {'c': 'default', 'f': 'event_handler'}
    elif table == 'eventitem':
        murl = {'c': 'default', 'f': 'event_item_handler'}
    else:
        murl = {}
    return LOAD(ajax_trap=True, user_signature=True, args=margs, vars=mvars, **murl)


#@auth.requires_signature()
def event_item_handler():
    if request.args:
        mid = int(request.args[0])
    db.event_items.parent.default = mid
    form = SQLFORM(db.event_items, formstyle='bootstrap')
    if form.process().accepted:
        session.flash = 'Event item submitted!'
        # just reload the whole page 
        redirect(URL(c='default', f='events', args=[mid], vars={'a': 'show'},
                                            user_signature=True), client_side=True)
    elif form.errors:
        response.flash = 'Errors in event form!'
    return dict(form=form)


#@auth.requires_signature()
def event_handler():
    d = None
    form = None
    rows = []
    action = request.vars.a
    if request.args:
        mid = int(request.args[0])
    else:
        mid = None
    if action == 'delete':
        if mid:
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
            response.flash = 'Event submitted!'
            redirect(URL(c='default', f='event_handler', args=[form.vars.id],
                            vars={'a': 'show'}, user_signature=True))
        elif form.errors:
            response.flash = 'Errors in event form!'
    elif action == 'show':
        mid = int(request.args[0])
        record = db.events(mid)
        if record is None:
            response.flash = 'Something went wrong!'
        rows = db(db.event_items.parent==record.id).select()
    else:
        raise ValueError
    return dict(record=record, form=form, action=action, rows=rows)


@auth.requires_signature()
def delete_event_item():
    mid = int(request.args[0])
    db(db.event_items.id==mid).delete()
    return "$('tr#event_item_{0}').remove();".format(mid)


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



