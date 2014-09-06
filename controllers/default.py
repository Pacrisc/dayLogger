# -*- coding: utf-8 -*-

# redirect to the login page by default
if not auth.user and request.function != 'user':
    redirect(URL(c='default', f='user', args=['login']))

def index():
    """
    """
    count_op = db.events.id.count()
    q = db.events.id>0
    if not auth.has_membership('admin'):
        q &= db.events.created_by == auth.user_id
    rows = db(q).select(db.events.ALL, count_op,
                        groupby=db.events.occured.day())
    return dict(rows=rows, count_op=count_op)


def day():
    """
    """
    if len(request.args) == 3:
        year, month, day = request.args
        q = db.events.occured.year()==year
        q &= db.events.occured.month()==month
        q &= db.events.occured.day()==day
        if not auth.has_membership('admin'):
            q &= db.events.created_by == auth.user_id
        rows = db(q).select(orderby=db.events.occured)
        return dict(rows=rows)

    session.flash = 'Wrong arguments for the day page!'
    redirect(URL(c='default', f='index'))


def events():
    """
    """
    return dict()

@auth.requires_signature()
def event_handler():
    if not request.args or request.vars.edit:
        editable = True
        fields = [field for field in db.events]
        fields.insert(4, Field('tags','string', label='Tags'))
        form = SQLFORM.factory(*fields,
            formstyle='bootstrap'
          )
        if form.process().accepted:
            db.events.insert(**db.events._filter_fields(form.vars))
    else:
        editable = False
        mid = int(request.args[0])
        form = db.events(mid)
        if form is None:
            response.flash = 'Something went wrong!'
    return dict(form=BEAUTIFY(form), editable=editable)



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
