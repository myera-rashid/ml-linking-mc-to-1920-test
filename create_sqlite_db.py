#simple script to try the connection to my new db as in here:https://suhas.org/sqlalchemy-tutorial/?fbclid=IwAR1xxpxCNy-63KGeSISXYsUIoWiEuykktUWxrYkZEvq3E79hCUt7MlKoeZA

import os
import sqlalchemy
import pandas as pd
#from app_for_nber.models import * # import model of tables from model.py
import sys
sys.path.append("/Users/myerarashid/Dropbox/MassMobility/app_for_hand_linking")
from models import * # import model of tables from model.py

#from app_for_nber.ml_linking import ml_linking # import app "ml_linking" from ml_linking.py
from ml_linking import ml_linking # import app "ml_linking" from ml_linking.py

#--------------------------------------------------------------------------------------
# Set paths

name = "/Users/myerarashid/Dropbox/MassMobility/app_for_hand_linking/dbs/dbase/test.db" # test in local dropbox 

path_example_tables = "/Users/myerarashid/Dropbox/MassMobility/app_for_hand_linking/datasets/" #Location of tables I upload to the DB

#--------------------------------------------------------------------------------------
###########################################################################
##DELETE TABLE IF IT EXISTS (BE CAREFUL when RUNNING THIS AGAIN)
exists = os.path.isfile(name)
if exists:
    #os.remove(name) #DELETE TABLE IF IT EXISTS (un-comment this part only when you want to delete database)
    print("File exists, lets remove it")
else: 
    print("File does not exist, lets create it")
###########################################################################


# 1. Create dbase or connect to if it already exists

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    url = 'sqlite:///'+db_file
    #url = url.format(db_file)

    # The return value of create_engine() is our connection object
    con = sqlalchemy.create_engine(url) #in my examples I checked this creates db if it doesn't exist

    # We then bind the connection to MetaData()
    meta = sqlalchemy.MetaData(bind=con, reflect=True)

    return con, meta

con, meta = create_connection(name) #first connection to create dataset


# 2. Create model of tables (Do I really need to do this? yes! see try_conn... and try_conn...2)


db.init_app(ml_linking) # initialize the app ml_linking
db.create_all(app=ml_linking) # create all tables from models.py associated to the app ml_linking


# 3. Connect again and check database and tables
con, meta = create_connection(name) #second connection to check tables exits

## check tables exist
print("Check tables exist:")
for table in meta.tables:
    print(table)

## check columns are correctly defined (in this case just for result
table_results = meta.tables['base_results']

print("Check columns in base_results")
for col in table_results.c:
    print(col)


# 4. Upload tables
#base_a:
df = pd.read_excel(path_example_tables+'datasetA_MC_multiplehit.xlsx')
df.to_sql(name="base_a", con=con, if_exists='append', index=True, index_label="id")

#base_b:
df = pd.read_excel(path_example_tables+'datasetB_1920_multiplehit.xlsx')
df.to_sql(name="base_b", con=con, if_exists='append', index=True, index_label="id")

#base_potmatches:
df = pd.read_excel(path_example_tables+'potentialAB_mc_1920_multiplehit.xlsx')
df.to_sql(name="base_potmatches", con=con, if_exists='append', index=True, index_label="id")

#base_results:
df = pd.read_excel(path_example_tables+'base_results_mc_1920_multiplehit.xlsx')
df.to_sql(name="base_results", con=con, if_exists='append', index=True, index_label="id")

#base_users:
df = pd.read_excel(path_example_tables+'base_users.xlsx')
df.to_sql(name="users", con=con, if_exists='append', index=True, index_label="id")


# 5. Check data was appended correctly

con, meta = create_connection(name)

## create tables in python
table_a = meta.tables['base_a']
table_b = meta.tables['base_b']
table_potmatches = meta.tables['base_potmatches']
table_results = meta.tables['base_results']
table_users = meta.tables['users']

## select and print them

print("Check values in each table, after append")

print("base_a")
for row in con.execute(table_a.select()):
    print(row)

print("base_b")
for row in con.execute(table_b.select()):
    print(row)

print("base_potmatches")
for row in con.execute(table_potmatches.select()):
    print(row)

print("base_results")
for row in con.execute(table_results.select()):
    print(row)

print("base_users")
for row in con.execute(table_users.select()):
    print(row)


### save results back to excel
#df = pd.read_sql_query("select * from base_results;", con)
#df.to_excel(r'/Users/myerarashid/Dropbox/MassMobility/app_for_hand_linking/results_backup.xlsx', index = False)



# 6. close connection
con.dispose()

