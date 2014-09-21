#!/usr/bin/python
# -*- coding: utf-8 -*-
from gluon.serializers import json

def index():
    return dict()


def bar_plot():
    return dict()

def bar_plot_data():
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
