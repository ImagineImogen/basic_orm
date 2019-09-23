from basic_orm import Table
import sqlite3

class Artist(Table):
    __tablename__ = "artist"
    artistid = {'type': 'integer', "auto_add": True, "primary_key": True}
    artisttype = {"type": "string", "length": 50}
    artistname = {"type": "string", "length": 50}

class Track(Table):
    __tablename__ = "track"
    trackid = {'type': 'integer'}
    trackname = {"type": "string", "length": 50}
    trackartist = {'type': 'integer'}
    trackartist.update({'foreign_key' : 'artistid'})


Artist.create_table()
Track.create_table()
Artist.add({'artisttype': 'popmusic','artistname':'Britney Spears'})
Artist.add({'artisttype': 'rock','artistname':'System of a Down'})
Artist.add({'artisttype': 'classical','artistname':'Fransz List'})
Track.add({'trackid': 1,'trackname':'Toxic', 'trackartist':1})
Track.add({'trackid': 2,'trackname':'Arials', 'trackartist':2})
Track.add({'trackid': 3,'trackname':'Mazeppa', 'trackartist':3})
Artist.select()
Track.select() #outputs an autojoined table
Track.select('trackname', 'trackartist')
Artist.update_all({'artisttype': "deathmetal", 'artistname':'Slipknot', 'albumscount': '10',}) #albumcount field doesn't exist
Artist.update_one({'artisttype': "postpunk", 'artistname':'Nick Cave'}, {'artistid' : 2 })
Track.select('trackname', 'trackartist')
Artist.select({"artistid": 2,"name": "Nick Cave"})
Track.select("trackartist", {"trackid": 2,"name": "Arials"})
Artist.select()
Artist.close()
Track.close()