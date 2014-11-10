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


def db_query_as_dict(user_id=None, group_id=None, begin_date=None, end_date=None, tags=None, view='nested'):
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
       - view: how to return results:
            * 'nested': nested dict (default)
            * 'flat': simple dict: items are passed as keys to the return dict
            * 'DataFrame': pandas.DataFrame , assumes group_id is not None
    """
    q = db.event_items.parent==db.events.id
    if begin_date:
        q &= db.events.edate>=begin_date
    if end_date:
        q &= db.events.edate<=end_date
    if user_id:
        q &= (db.events.created_by==user_id) 
    if group_id:
        q &= (db.events.parent_id==group_id)

    if tags:
        tags_ids = db(db.tags.name.belongs(tags)).select().as_dict().keys()
        q &= db.tag_event_items.parent==db.event_items.id
        q &= db.tag_events.parent==db.events.id
        q &= (db.tag_events.tag.belongs(tags_ids) | db.tag_event_items.tag.belongs(tags_ids))


    # get id of all the events in the query
    events_id = db(q).select(db.events.id, groupby=db.events.id).as_dict().keys()

    q = db.events.id.belongs(events_id)
    events = db(q).select(db.events.id, db.events.title, db.events.parent_id,
            db.events.edatetime, db.events.created_by).as_dict()

    group_id_list = []

    if view == 'nested':
        for eid, event in events.iteritems():
            sub_q =  (db.tag_events.parent==eid) & (db.tags.id==db.tag_events.tag)
            event['tags'] = [el['name'] for el in db(sub_q).select(db.tags.name).as_list()]
            sub_q = db.event_items.parent==eid
            sub_res = db(sub_q).select(db.event_items.description, db.event_items.value).as_list()
            event['items'] = sub_res

            event['id'] = eid
    elif view in ['flat', 'DataFrame']:
        for eid, event in events.iteritems():
            if event['parent_id'] not in group_id_list:
                group_id_list.append(event['parent_id'])
            sub_q =  (db.tag_events.parent==eid) & (db.tags.id==db.tag_events.tag)
            event['tags'] = [el['name'] for el in db(sub_q).select(db.tags.name).as_list()]
            sub_q = db.event_items.parent==eid
            sub_res = db(sub_q).select(db.event_items.id, db.event_items.description, db.event_items.value).as_list()
            event['lookup'] = {'id': eid}
            for item in sub_res:
                event[item['description']] = item['value']
                event['lookup'][item['description']] = item['id']

            event['id'] = eid
    else:
        raise ValueError("Not implemented: view = {} not in ['nested', 'flat']!")

    if view in ['nested', 'flat']:
        return events.values()
    elif view == 'DataFrame':
        import pandas
        res = []
        for group_id_el in group_id_list:
            res_el = {}
            group_events = filter(lambda x: x['parent_id'] == group_id_el,  events.values())
            res_el = {key: group_events[0][key] for key in ['title', 'parent_id', 'tags']}
            lookup_el = [group_el['lookup'] for group_el in  group_events]
            df = pandas.DataFrame(group_events)
            lookup_df =  pandas.DataFrame(lookup_el)
            for key in ['title', 'parent_id', 'tags']:
                del df[key]

            df['edatetime'] = pandas.to_datetime(df['edatetime'])#, format='%Y-%m-%d  %H:%M:%S.%f')
            df.index = df.id
            lookup_df.index = df.id
            del df['id']
            del df['lookup']
            del lookup_df['id']
            res_el['items']  = df
            res_el['lookup'] = lookup_df

            res.append(res_el)
        if group_id is not None:
            return res[0]
        else:
            return res




