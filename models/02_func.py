#!/usr/bin/python
# -*- coding: utf-8 -*-

def date2str(date):
    return str(date)

def str2date(date_str):
    import datetime
    try:
        dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return dt.date()
    except:
        return None

def has_item_permission(row):
    if is_admin or not row:
        return True
    elif row.created_by == auth.user.id or row.modified_by == auth.user.id:
        return True
    else:
        return False


def db_query_as_dict(user_id=None, begin_date=None, end_date=None, tags=None):
    """
    Stitch together various tables and return data in a nested dict structure
    for visualization. 

    This prototype version uses nested querries (not efficient, not scalable etc..) ->
    for a total of Nevents*2 MySQL selects so
    using only for beta version. Need to think about a better way of doing this (basically
    stitching 6 tables together to get a BSON like structure).

    Parameters:
    -----------
       - user_id: int: for exemple auth_user.id
       - beging_date, end_date: date:  date  interval
       - tags: list of tags
       - datatime2s: convert datetime to seconds since origin
    """
    q = db.event_items.parent==db.events.id
    if begin_date:
        q &= db.events.edate>=begin_date
    if end_date:
        q &= db.events.edate<=end_date
    if user_id:
        q &= (db.events.created_by==user_id) 

    if tags:
        tags_ids = db(db.tags.name.belongs(tags)).select().as_dict().keys()
        q &= db.tag_event_items.parent==db.event_items.id
        q &= db.tag_events.parent==db.events.id
        q &= (db.tag_events.tag.belongs(tags_ids) | db.tag_event_items.tag.belongs(tags_ids))


    # get id of all the events in the query
    events_id = db(q).select(db.events.id, groupby=db.events.id).as_dict().keys()

    q = db.events.id.belongs(events_id)
    events = db(q).select(db.events.id, db.events.title, db.events.parent,
            db.events.edatetime, db.events.created_by).as_dict()

    for eid, event in events.iteritems():
        sub_q =  (db.tag_events.parent==eid) & (db.tags.id==db.tag_events.tag)
        event['tags'] = [el['name'] for el in db(sub_q).select(db.tags.name).as_list()]
        sub_q = db.event_items.parent==eid
        sub_res = db(sub_q).select(db.event_items.description, db.event_items.value).as_list()
        event['items'] = sub_res

        #event['items'] = {el['key: val for 
        #event['parent'] = event['parent']
        event['id'] = eid

    return events.values()

