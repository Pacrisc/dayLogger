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



