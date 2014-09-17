#!/usr/bin/python
# -*- coding: utf-8 -*-

if not auth.user:
    redirect(URL(c='default', f='user', args=['login']))


def uploadimage():
    parent_id = int(request.vars.parent_id)
    dbtable = db.pictures          #uploads table name
    def makeThumbnail(dbtable,ImageID,parent_id, size=(150,150)):
        try:    
            thisImage=db(dbtable.id==ImageID).select()[0]
            import os, uuid
            from PIL import Image
        except: return
        im=Image.open(request.folder + 'uploads/' + thisImage.mainfile)
        im.thumbnail(size,Image.ANTIALIAS)
        thumbName='uploads.thumb.%s.jpg' % (uuid.uuid4())
        im.save(request.folder + 'uploads/' + thumbName,'jpeg')
        thisImage.update_record(thumb=thumbName, event=parent_id)
        return 
    if len(request.args):
        records = db(dbtable.id==request.args[0]).select()
    if len(request.args) and len(records):
        form = SQLFORM(dbtable, records[0], deletable=True)
    else:
        form = SQLFORM(dbtable)
    if form.accepts(request.vars, session): 
        response.flash = 'form accepted'
        makeThumbnail(dbtable,form.vars.id, parent_id, (175,175))
        #return 'console.log("ok");'
        return 'window.location.reload();'
    elif form.errors:
        response.flash = 'form has errors'
    ## Quick list just to demonstrate...
    #plist  = db(dbtable).select()
    plist  = db(dbtable.event==parent_id).select()
    return dict(form=form,plist=plist, parent_id=parent_id)

