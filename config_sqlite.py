#config file for SQLite


name = "/Users/myerarashid/Dropbox/MassMobility/app_for_hand_linking/dbs/dbase/test.db" # test in local dropbox 


SECRET_KEY = 'any_key_works' # keep this key secret during production
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + name

SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
