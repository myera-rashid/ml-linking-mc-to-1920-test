# Here I create the structure of the database and its tables

from flask_sqlalchemy import SQLAlchemy
import datetime

# create a new SQLAlchemy object
db = SQLAlchemy()

# Base model that for other models to inherit from

class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.String(100), primary_key=True, nullable=True)


########################################################################
#Linking:

# Table for records from A
class base_a(Base):
    idA = db.Column(db.String(100))
    man_first_nameA = db.Column(db.String(100))
    man_last_nameA = db.Column(db.String(100))
    man_yobA = db.Column(db.Integer)
    wife_first_nameA = db.Column(db.String(100))
    wife_yobA = db.Column(db.Integer)

    # user friendly way to display the object
    def __repr__(self):
        return self.idA

# Table for records from B
class base_b(Base):
    idB = db.Column(db.String(100))
    man_first_nameB = db.Column(db.String(100))
    man_last_nameB = db.Column(db.String(100))
    man_yobB = db.Column(db.Integer)
    wife_first_nameB = db.Column(db.String(100))
    wife_yobB = db.Column(db.Integer)

    # user friendly way to display the object
    def __repr__(self):
        return self.idB

# Table for potential matches (candidates from B for record in A)
class base_potmatches(Base):
    idA = db.Column(db.String(100)) #, db.ForeignKey('base_a.idA')
    idB = db.Column(db.String(100)) #, db.ForeignKey('base_b.idB')
    jscore = db.Column(db.Integer)
    to_drop_jscore = db.Column(db.Integer)


# Table for links done (results)
class base_results(Base):
    trained = db.Column(db.Integer)
    idA = db.Column(db.String(100)) #, db.ForeignKey('base_a.idA')
    result_idB = db.Column(db.String(100)) #this can be idB or "no_match", or "multiple"
    time_start = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=True)
    time_end = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=True)
    user = db.Column(db.String(100))
    first_2link = db.Column(db.Integer)


    # user friendly way to display the object
    def __repr__(self):
        return self.trained



########################################################################
#Logins:

# Table to add more users/ra's
class User(Base):
    """"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

    # ----------------------------------------------------------------------
    def __init__(self, username, password):
        """"""
        self.username = username
        self.password = password

# Table to track logins
class Track_logins(Base):
    """"""
    __tablename__ = "track_logins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    login_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=True)

    def __init__(self, username, login_date):
        """"""
        self.username = username
        self.login_date = login_date



