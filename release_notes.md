Nov 10th 2014
=============

What's new
----------
  - added a table to store algoritms that process data before visualization
  - template page for managing algorithms
  - adapted a simple time dependent plot to be used together with this new system (single or repeat events + processing algorithm)


Nov 5th 2014
=============


What's new
----------
  
  - ability to clone events
  - changed event_items.value field type from integer to double 
  - added events.comment field (not used for the moment)
  - there is now two type of events: *one time event* and *repeat events*. The former ones are completely undependent, while the later ones are created as a clone of an existing event, and have the same item structure.
         - In a repeat event, the modification of the following fields will be applied to all of it's member (i.e. will affect events on different days): title, description, tags, delete or add event items, event item's description. 
         - On the other hand,  photos, comment and event item's values are specific to any member of the group.
         - It is possible to transform one of the members of the repeat event group into a one time event (unlink button). This operation is at present permanent and  cannot be cancelled.
  - repeat events have 2 view modes: default view (same as before) and table view where all of the events in this group are displayed on one page.

Upgrade notes
------------

  * Moved DB login info ito a separate file `models/000_private.py` from `models/00_db.py` to avoid to have to do merges every time the `00_db.py` is modified (contains the tables structure). The upgrade notes are as follows:
       
       1. Save your login information contained in  `models/00_db.py`
       2.  `git pull`
       3. Fill `models/000_private.py` with correct information (if applicable)
       4. Ignore file from git updates
          `git update-index --assume-unchanged ./models/000_private.py`


 * If using a legacy database with existing user data, please run:
    
            python web2py.py -S dayLogger -M
            db(db.events.parent_id==None).update(parent_id=db.events.id)

   in order to correctly initialize the new `parent_id` field.
 
