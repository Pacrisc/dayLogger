# -*- coding: utf-8 -*-

if not auth.user:
    redirect(URL(c='default', f='user', args=['login']))

@auth.requires_membership('admin')
def users():
    db.auth_user.registration_key.readable=True
    grid = SQLFORM.grid(db.auth_user,
                   fields=[db.auth_user.id, db.auth_user.first_name,
                           db.auth_user.last_name, db.auth_user.registration_key, db.auth_user.email],
                   orderby = [~db.auth_user.id]
                   )
    return locals()

@auth.requires_membership('admin')
def impersonate():
    if request.vars.uid:
        uid = int(request.vars.uid)
        session.imp_user = db(db.auth_user.id == uid).select().first()
        if not session.imp_user:
            raise ValueError
        redirect(URL('default', 'index'))
    else:
        if session.imp_user:
            del session.imp_user
            redirect(URL('madmin', 'users'))

@auth.requires_membership('admin')
def tags():
    grid = SQLFORM.grid(db.tags)

    Ntags = db(db.tags).count()

    return dict(grid=grid, Ntags=Ntags)

@auth.requires_signature()
@auth.requires_membership('admin')
def prepopulate_tags():
# prepopulate tags table
    if not db(db.tags).count():
        with open('./applications/dayLogger/modules/nounlist.txt', 'r') as f:
            for line in f:
                db.tags.insert(name=line.strip())
        return 'window.location.reload();'
    else:
        return ''


def prepopulate_db():
    return dict()


@auth.requires_signature()
@auth.requires_membership('admin')
def prepopulate_db_api():
    # this prepopulates database (including auth_user) with random data
    # necessary to work on visualizations (need something to visualize)
    from applications.dayLogger.modules.pypsum import get_lipsum
    import random
    import string

    lipsum = lambda n, what : get_lipsum(n, what, 'no')[0]


    def random_string(length=8, chars=string.letters + string.digits):
        return ''.join([random.choice(chars) for i in range(length)])
    
    def random_date(start='09/1/2014 9:00 AM', end='9/15/2014 9:00 AM'):
        start = datetime.datetime.strptime(start, '%m/%d/%Y %I:%M %p')
        end = datetime.datetime.strptime(end, '%m/%d/%Y %I:%M %p')
        return start + datetime.timedelta(
            seconds=random.randint(0, int((end - start).total_seconds())))

    
   
    N_users = 5 # exact number of users
    N_events = 20 # max number of events per user
    N_event_items = 5 # max number of events per user
    N_avail_tags = 20
    N_tags_per_item = 2


    # prepopulate tags
    if not db(db.tags).count():
        with open('./applications/dayLogger/modules/nounlist.txt', 'r') as f:
            for line in f:
                db.tags.insert(name=line.strip())
    tags_id_list = range(1,N_avail_tags)

    for user_idx in range(N_users):
        user_id = db.auth_user.insert(last_name=random_string(5), first_name=random_string(5),
                        email=random_string(5)+'@not-existing.io',)
        for event_idx in range(random.randint(1,N_events)):
            event_date = random_date()
            # create event
            event_id = db.events.insert(title=lipsum(1, 'words'),
                                        description=lipsum(1, 'paras'),
                                        edate=event_date.date(),
                                        etime=event_date.time(),
                                        created_by=user_id,
                                        modified_by=user_id)
            # create tags for events
            for tag_idx in range(random.randint(1,N_tags_per_item)):
                db.tag_events.insert(parent=event_id, tag=random.randint(1,N_avail_tags))

            for event_item_idx in range(random.randint(1,N_event_items)):
                event_item_id = db.event_items.insert(parent=event_id, 
                                                      description=random_string(10, string.letters + ' '),
                                                      value=random.randint(0,100))
                for tag_idx in range(random.randint(1,N_tags_per_item)):
                    db.tag_event_items.insert(parent=event_item_id, tag=random.randint(1,N_avail_tags))
    redirect(URL(c='default', f='index', user_signature=True), client_side=True)

