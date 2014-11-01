# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()
from gluon.tools import prettydate
import datetime
from imageutils import THUMB

db = DAL(DB_LOGIN,             #'sqlite://storage.sqlite',
        pool_size=1,check_reserved=['mysql'])

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

# plugins.wiki.level = 2
# plugins.wiki.editor = False

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else 'smtp.gmail.com:587'
mail.settings.sender = EMAIL_SENDER
mail.settings.login = EMAIL_LOGIN

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = True
auth.settings.reset_password_requires_verification = True


hidden = {'readable': False, 'writable': False}


db.define_table('events',
    Field('title', 'string', requires=IS_NOT_EMPTY()),
    Field('description', 'text', requires=IS_NOT_EMPTY()),
    Field('edate', 'date', label='Date', requires=IS_DATE()),
    Field('etime', 'time', label='Time', requires=IS_TIME()),
    Field('edatetime', compute=lambda r: datetime.datetime.combine(r['edate'],r['etime'])),
    #Field('edatetime2s', compute=lambda r: r['edatetime'].strftime('%s') ),
    auth.signature
    )

db.events.edate.widget = SQLFORM.widgets.date.widget
#db.events.etime.widget = SQLFORM.widgets.time.widget

db.define_table('event_items',
    Field('parent', 'reference events', **hidden),
    Field('description', 'string', requires=IS_NOT_EMPTY()),
    Field('value', 'integer', requires=IS_NOT_EMPTY())
    )

db.define_table('tags',
    Field('name', 'string', requires=IS_NOT_EMPTY())
    )

db.define_table('tag_events',
    Field('parent', 'reference events'),
    Field('tag', 'reference tags'))

db.define_table('tag_event_items',
    Field('parent', 'reference event_items'),
    Field('tag', 'reference tags'))


db.define_table('pictures',
    Field('name','string'),
    Field('mainfile','upload'),
    Field('size', 'list:integer', **hidden),
    Field('thumb','upload', **hidden),
    Field('event', 'reference events', **hidden),
    auth.signature
    )
db.pictures.thumb.compute = lambda row: THUMB(row.mainfile, 200, 200)

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
#from gluon.contrib.login_methods.janrain_account import use_janrain
#use_janrain(auth, filename='private/janrain.key')


## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
