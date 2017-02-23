from google.appengine.ext import ndb

class Message(ndb.Model):
    receiver = ndb.StringProperty()
    sender = ndb.StringProperty()
    subject = ndb.TextProperty()
    text = ndb.TextProperty()
    author = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    deleted = ndb.BooleanProperty(default=False)