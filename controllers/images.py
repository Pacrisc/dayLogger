#!/usr/bin/python
# -*- coding: utf-8 -*-

def makeThumbnail(dbtable,ImageID,size=(150,150)):
    try:    
        thisImage=db(dbtable.id==ImageID).select()[0]
        import os, uuid
        from PIL import Image
    except: return
    im=Image.open(request.folder + 'uploads/' + thisImage.mainfile)
    im.thumbnail(size,Image.ANTIALIAS)
    thumbName='uploads.thumb.%s.jpg' % (uuid.uuid4())
    im.save(request.folder + 'uploads/' + thumbName,'jpeg')
    thisImage.update_record(thumb=thumbName)
    return 

def uploadimage():
    dbtable = db.uploads          #uploads table name
    if len(request.args):
        records = db(dbtable.id==request.args[0]).select()
    if len(request.args) and len(records):
        form = SQLFORM(dbtable, records[0], deletable=True)
    else:
        form = SQLFORM(dbtable)
    if form.accepts(request.vars, session): 
        response.flash = 'form accepted'
        makeThumbnail(dbtable,form.vars.id,(175,175))
    elif form.errors:
        response.flash = 'form has errors'
    ## Quick list just to demonstrate...
    list = crud.select(dbtable)
    return dict(form=form,list=list)

