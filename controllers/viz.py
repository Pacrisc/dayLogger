#!/usr/bin/python
# -*- coding: utf-8 -*-
from gluon.serializers import json

if not auth.user:
    redirect(URL(c='default', f='user', args=['login']))

DATE_FMT = '%m/%d/%Y'
strptime = datetime.datetime.strptime

def index():
    return dict()


def bar_plot():
    return dict()

def scatter_plot():
    import random
    import string
    def random_string(length=8, chars=string.letters + string.digits):
        return ''.join([random.choice(chars) for i in range(length)])

    return dict(pageid=random_string(10))

def scatter_plot_data():
    from itertools import cycle
    import calendar

    if session.imp_user:
        user_id = session.imp_user.id
    else:
        user_id = auth.user.id
    if not request.vars.page:
        raise HTTP(403)
    session_page = 'scatter_{0}'.format(request.vars.page)

    if session_page in session:
        mquery = session[session_page]
    else:
        mquery = {'end': None, 'begin': None, 'tags': []}
        session[session_page] = mquery
    #try:
    if request.vars.begin_date:
        mquery['begin'] = strptime(request.vars.begin_date, DATE_FMT)
    if request.vars.end_date:
        mquery['end'] = strptime(request.vars.end_date, DATE_FMT)
    if request.vars.tag and request.vars.action in ['add', 'delete']:
        tag_name = request.vars.tag
        if request.vars.action == 'add':
            mquery['tags'].append(tag_name)
        elif request.vars.action == 'delete' and tag_name in mquery['tags']:
            mquery['tags'].remove(tag_name)
    #except Exception:
    #    raise HTTP(403)

    res = db_query_as_dict(user_id, mquery['begin'], mquery['end'], mquery['tags'])

    shapes = cycle(['circle', 'cross', 'triangle-up', 'triangle-down', 'diamond', 'square'])
    data = []
    tags = []
    for row in res:
        values = []
        for item in row['items']:
            out = {}
            edate = strptime(row['edatetime'], '%Y-%m-%d %H:%M:%S')

            out['x'] = calendar.timegm(edate.utctimetuple())*1000
            out['y'] = item['value']
            out['label'] = item['description']
            out['shape'] = shapes.next()
            values.append(out)
            tags += row['tags']
        data.append({'key': row['title'], 'values': values, 'tags': row['tags']}) 
    tags = list(set(tags))
    return dict(data={'data': data, 'tags': tags})



def api():
    user_id = None
    begin_date = None
    end_date = None
    tags = None
    if request.vars.user_id:
        user_id = int(request.vars.user_id)
    if request.vars.begin_date:
        begin_date = strptime(request.vars.begin_date, DATE_FMT)
    if request.vars.end_date:
        end_date = strptime(request.vars.end_date, DATE_FMT)
    if request.vars.tags:
        tags = request.vars.tags.split(',')

    res = db_query_as_dict(user_id, begin_date, end_date, tags)

    return dict(data=res)


def bar_plot_data():
    """ This is a very preliminary case """
    d = []
    user_id = session.imp_user and session.imp_user.id or auth.user.id

    q = db.tag_event_items.parent==db.event_items.id
    q &= db.tag_event_items.tag==db.tags.id
    q &= db.event_items.parent==db.events.id
    q &= db.events.created_by==user_id 

    op = {}
    op['sum'] = db.event_items.value.sum()
    op['min'] = db.event_items.value.min()
    op['max'] = db.event_items.value.max()
    op['count'] = db.event_items.value.count()
    rows = db(q).select(db.tags.ALL,
            *[op[key] for key in op],
            groupby=db.tags.id)
    opw = {}
    opw['min'] = lambda row: row[op['min']]
    opw['max'] = lambda row: row[op['max']]
    opw['avg'] = lambda row: 1.0*row[op['sum']]/row[op['count']]

    colors = {'min': '#d67777', 'avg': '#4f99b4', 'max': '#FF7F0E'} 
    for op_key in ['min', 'max', 'avg']:
        out = {"key": op_key,
               "color": colors[op_key]}
        values = []
        for row in rows:
            values.append({"label" : row.tags.name ,
                       "value" : opw[op_key](row) })
        out['values'] = values
        d.append(out)
    return dict(data=d)
