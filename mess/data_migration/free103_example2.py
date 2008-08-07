# Another example from free103.

import re
import MySQLdb
import datetime
import time

import sys
sys.path.insert(0, '/home/free103/django')

from free103.awe.models import Location, EventType, Event, Artist
from util import html_unescape

phone_re = re.compile(r'\D')

conn = MySQLdb.connect(host='sql.free103point9.org', user='free103_app', 
        db='**********', passwd='*********', charset='latin1')
try:
    # old to new database, 1609-1626 -> 1664-1680
    sql = "SELECT * FROM Event WHERE ActiveFlag!=-1 AND EventID>1613 AND EventID<1627"
    curs = conn.cursor()
    curs.execute(sql)
    while (1):
        result = curs.fetchone()
        if result == None:
            break
        result_list = []
        for field in result:
            if field:
                pass
            elif field == 0:
                pass
            else:
                field = u''
            result_list.append(field)
        result = tuple(result_list)
        event_id, type_id, active, ongoing, admission, name, description, extra_artists, press_release, location, location_url, address, address2, city, state_id, country_id, postal_code, phone, url, start, end = result
        print 'Processing %s ...' % name.encode('ascii', 'replace'),
        this_location = (location, location_url, address, address2, city, state_id, country_id, postal_code, phone)
        # keep state table?
        # no, use django.contrib.localflavor.us to validate form
        if state_id:
            state_sql = "SELECT StateAbbr FROM State WHERE StateID=%s"
            state_curs = conn.cursor()
            state_curs.execute(state_sql, state_id)
            state = state_curs.fetchone()[0]
        else:
            state = u''
        if country_id:
            country_sql = "SELECT CountryName FROM Country WHERE CountryID=%s"
            country_curs = conn.cursor()
            country_curs.execute(country_sql, country_id)
            country = country_curs.fetchone()[0]
        else:
            country = u''
        if phone:
            phone = phone_re.sub('', phone)
            phone_list = [phone[0:3], '-', phone[3:6], '-', phone[6:10]]
            phone = ''.join(phone_list)
        type = EventType.objects.get(id=type_id)
        loc_list = Location.objects.filter(name=location).filter(url=location_url).filter(address=address).filter(address2=address2).filter(city=city).filter(state=state).filter(country=country).filter(postal_code=postal_code).filter(phone=phone)
        if loc_list:
            location = loc_list[0]
        else:
            loc = Location(name=html_unescape(location), url=location_url, address=address, address2=address2, city=city, state=state, country=country, postal_code=postal_code, phone=phone)
            loc.save()
            location = loc
        if start.time() == datetime.time(0, 0, 1):
            start_time = None
        else:
            start_time = start.time()
            
        # null ends were set to '0000-00-00 00:00:01', which
        # shows up as a string because it can't be parsed
        # as a date
        try:
            end_date = end.date()
            if end.time() == datetime.time(0, 0, 1):
                end_time = None
            else:
                end_time = end.time()
        except AttributeError:
            end_date = datetime.date(9999, 12, 31)
            end_time = None

        if not admission:
            admission = None

        if url and url[:7] != 'http://':
            url = 'http://' + url

        e = Event(
                # give new IDs because of overlap between old and new
                #id=id, 
                name=html_unescape(name), 
                active=active, 
                ongoing=ongoing, 
                admission=admission, 
                brief_description=html_unescape(description), 
                extra_artists=html_unescape(extra_artists), 
                long_description=html_unescape(press_release), 
                url=url, 
                start_date=start.date(), 
                start_time=start_time,
                end_date=end_date,
                end_time=end_time,
                #type=type, now m2m field
                #location=location, now m2m field
            )
        e.save()
        print 'saved, id=%s ...' % e.id,
        
        print 'adding type ...',
        e.types.add(type)
        print 'adding location ...',
        e.locations.add(location)

        print 'adding artists ...',
        artist_sql = "SELECT ArtistID FROM ArtistEventRelation WHERE EventID=%s"
        artist_curs = conn.cursor()
        artist_curs.execute(artist_sql, event_id)
        artist_id_set = artist_curs.fetchall()
        for result_tuple in artist_id_set:
            artist_id = result_tuple[0]
            artist = Artist.objects.get(id=artist_id)
            e.artists.add(artist)

        print 'done.'
finally:
    conn.close()

