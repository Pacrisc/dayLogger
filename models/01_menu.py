# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from gluon.tools import Wiki


#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo =  ''
response.title = 'Day Logger'
response.subtitle = 'A simple web2py day logger to track your daily biologically relevant events'

response.meta.author = 'rth <rth@crans.org>'
response.meta.keywords = ''
response.meta.generator = ''


left_sidebar_enabled = False
right_sidebar_enabled = False


## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default', 'index'), [])
]

is_admin = auth.has_membership('admin')

if is_admin:
    admin_menu = ('Admin', False, URL('madmin', 'users'), 
                    [('Users', False, URL('madmin', 'users')),
                     ('Tags', False, URL('madmin', 'tags')),])

    response.menu.append(admin_menu)
    if session.imp_user:
        response.menu.append(
            ('Stop impersonating ({0})'.format(session.imp_user.email), False, URL('madmin', 'impersonate'), []))











#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

if "auth" in locals(): auth.wikimenu() 

