#!/usr/bin/python
# -*- coding: utf-8 -*-

if not auth.user:
    redirect(URL(c='default', f='user', args=['login']))


def uploadimage():
    parent_id = int(request.vars.parent_id)
    dbtable = db.pictures          #uploads table name
    if len(request.args):
        records = db(dbtable.id==request.args[0]).select()
    if len(request.args) and len(records):
        form = SQLFORM(dbtable, records[0], deletable=True)
    else:
        form = SQLFORM(dbtable)
    if form.accepts(request.vars, session): 
        response.flash = 'form accepted'
        db(dbtable.id==form.vars.id).update(event=parent_id)
        #return 'console.log("ok");'
        return 'window.location.reload();'
    elif form.errors:
        response.flash = 'form has errors'
    ## Quick list just to demonstrate...
    #plist  = db(dbtable).select()
    plist  = db(dbtable.event==parent_id).select()
    return dict(form=form,plist=plist, parent_id=parent_id)

