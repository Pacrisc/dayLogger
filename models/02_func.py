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




