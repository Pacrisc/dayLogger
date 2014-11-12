#!/usr/bin/python
# -*- coding: utf-8 -*-
if not auth.user and request.function != 'user':
    redirect(URL(c='default', f='user', args=['login']))

def index():
    q = db.algorithms.id>0
    if not is_admin:
        q &= ((db.algorithms.created_by == auth.user_id) | (db.algorithms.visibility == 'public'))
    elif session.imp_user:
        q &= ((db.algorithms.created_by == session.imp_user.id) | (db.algorithms.visibility == 'public'))

    if request.vars.sortby is not None and request.vars.sortby in ['last', 'name', 'pending']:
        sortby = request.vars.sortby
    else:
        sortby = 'last'

    if sortby == 'last':
        orderby = db.algorithms.modified_on
    elif sortby == 'name':
        orderby = db.algorithms.title
    elif sortby == 'pending':
        q &= db.algorithms.status == 'pending'
        orderby = db.algorithms.modified_on
        #orderby = db.algorithms.status

    rows = db(q).select(db.algorithms.ALL, orderby=orderby)
    return dict(rows=rows, sortby=sortby)

@auth.requires_membership('admin')
@auth.requires_signature()
def authorize():
    if len(request.args) == 2 and request.args[1] in ['validated', 'forbidden']:
        mid = int(request.args[0])
        status = request.args[1]
        record = db.algorithms(mid)
    else:
        record = None

    if not record:
        raise HTTP('403')

    record.update_record(status=status)
    parent_el = "$('.dl_crud_toolbar .dropdown-toggle')"
    res = ' '.join(["{0}.removeClass('btn-{1}');".format(parent_el, key) for key in ['warning', 'ok', 'error']])
    res += "$('.dl_crud_toolbar .dropdown-toggle span.btn-label').text('{}');".format(status)
    if status == 'validated':
        return res + "{0}.addClass('btn-ok');".format(parent_el)
    elif status == 'forbidden': 
        return res + "{0}.addClass('btn-error');".format(parent_el)


def manage():
    d = None
    form = None
    rows = []
    vargs = {}
    action = request.vars.a
    if request.args:
        mid = int(request.args[0])
        if action in ['delete', 'update']:
            if not has_item_permission(db.algorithms(mid)):
                raise HTTP(403)
    else:
        mid = None
    if action == 'delete':
        if mid:
            res = db(db.algorithms.id == mid).delete()
            if res:
                redirect(URL('algorithms', 'index'), client_side=True)
    elif action in ['update', 'create']:
        if mid:
            record = db.algorithms(mid)
        else:
            record = None
        form = SQLFORM(db.algorithms, record, formstyle='bootstrap')
        if form.process().accepted:
            #session.flash = 'Event submitted!'

            redirect(URL(c='algorithms', f='manage', args=[form.vars.id],
                            vars={'a': 'show'}, user_signature=True))
        elif form.errors:
            response.flash = 'Errors in event form!'
        context = dict(form=form, record=record, action=action)
        return response.render('algorithms/manage_crupdate.html', context)

    elif action == 'show':
        mid = int(request.args[0])
        record = db.algorithms(mid)
        vargs = {}
        if request.vars.view and request.vars.view in ['default', 'summary']:
            view_mode = request.vars.view
        else:
            view_mode = 'default'

        vargs['view_mode'] = view_mode

        if record is None:
            response.flash = 'Something went wrong!'
        context = dict(record=record, form=form, **vargs)
        if view_mode in ['default']:
            return  response.render('algorithms/manage_show_full.html',  context)
        elif view_mode == 'summary':
            return  response.render('algorithms/manage_show_summary.html', context)
    else:
        raise HTTP(403)

