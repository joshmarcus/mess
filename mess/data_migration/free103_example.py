# An example for data migration taken from my work for free103.  Note that
# I was moving data from a MySQL database rather than Excel, as we'll be
# doing, but the going-into-Django parts should be demonstrative.

import MySQLdb

import sys
sys.path.insert(0, '/home/free103/django')

from free103.awe.models import Work, Artist

conn = MySQLdb.connect(host='sql.free103point9.org', user='free103_app', 
        db='********', passwd='*********')
try:
    sql = "SELECT SongID, ArtistID FROM SongArtistRelation"
    curs = conn.cursor()
    curs.execute(sql)
    while (1):
        result = curs.fetchone()
        if result == None:
            break
        song_id, artist_id = result
        try:
            work_obj = Work.objects.get(id=song_id)
        except Work.DoesNotExist:
            print 'Work for id %s doesn\'t exist.' % song_id
            continue
        artist_obj = Artist.objects.get(id=artist_id)
        print 'Adding %s to %s ...' % (artist_obj, work_obj),
        work_obj.artists.add(artist_obj)
        print 'done.'

finally:
    conn.close()
