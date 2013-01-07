import MySQLdb
import sys

host = "localhost"
username = "root"
password = "toor"
database = "GeoNames_US"
city_list_file = "US.txt"

db_conn = MySQLdb.connect(host, username, password)
try:
    db_conn.select_db(database)
    db_cursor = db_conn.cursor()
except Exception, e:
    print "Database '%s' not found... " % (database)
    create_db = raw_input("Create database '%s'? y/n: " %(database)).lower()
    if create_db == 'y':
        print "Creating database '%s'..." % (database)
        db_conn.execute("""CREATE DATABASE %s """ % (database))
        db_conn.select_db(database)
        db_cursor = db_conn.cursor()
    else: 
        print "Exiting..."
        sys.exit()

try:
    US_file = open(city_list_file)
    print "Successfuly openned file '%s'..." % (city_list_file)
except Exception, e:
    print "File '%s' doesnt exist, exiting..." % (city_list_file)
    sys.exit()

state_list = []
county_list = []
city_list = []

print "Organizing US city list into state/county/city..."
for US_line in US_file:
    line = US_line.split("\t")

    if not any(state.get('state_abbr', None) == line[4] for state in state_list):
        state = dict(state=line[3],
                     state_abbr=line[4])
        state_list.append(state)

    if not any(county.get('county', None) == line[5] for county in county_list):
        county = dict(county=line[5],
                      state=line[3],
                      state_abbr=line[4])
        county_list.append(county)

    city_dict = dict(country=line[0],
                     postal_code=int(line[1]),
                     place=line[2],
                     state=line[3],
                     state_abbr=line[4],
                     county=line[5],
                     latitude=float(line[9]),
                     longitude=float(line[10]))
    city_list.append(city_dict)

print "Got %s states / %s countys / %s cities..." %(len(state_list), len(county_list), len(city_list))

print "Creating state table..."
db_cursor.execute("""\
CREATE TABLE state ( \
id INT AUTO_INCREMENT, \
name VARCHAR(100) NULL, \
abbr VARCHAR(20) NULL, \
PRIMARY KEY(id)) \
""")

insert_states_query = """
INSERT INTO state (name, abbr) 
VALUES ('%s', '%s')
"""

print "Storing state values..."
for state in  state_list:
  if state['state'] != '':
      db_cursor.execute(insert_states_query % (state['state'], state['state_abbr']))

print "Creating county table..."
db_cursor.execute("""
CREATE TABLE county (
id INT NOT NULL AUTO_INCREMENT, 
county VARCHAR(100) NULL, 
state_id INT,
FOREIGN KEY (state_id) REFERENCES state(id), 
PRIMARY KEY (id))
""")

insert_county_query = """
INSERT INTO county (county, state_id)
VALUES (%s, %s)
"""

print "Storing county values..."
for county in county_list:
  db_cursor.execute("SELECT id from state where abbr = '%s'" % county['state_abbr'])
  data = db_cursor.fetchone()
  if data:
      db_cursor.execute(insert_county_query, (county['county'], data[0]))

print "Creating city table..."
db_cursor.execute("""
CREATE TABLE city (
id INT NOT NULL AUTO_INCREMENT,
name VARCHAR(100),
postal_code INT NOT NULL,
latitude DOUBLE NOT NULL,
longitude DOUBLE NOT NULL,
state_id INT,
county_id INT,
FOREIGN KEY (state_id) REFERENCES state(id),
FOREIGN KEY (county_id) REFERENCES county(id),
PRIMARY KEY (id))
""")

insert_county_query = """
INSERT INTO city (name, postal_code, latitude, longitude, state_id, county_id)
VALUES (%s, %s, %s, %s, %s, %s)
"""

print "Storing city values (this may take a while)..."
for city in city_list:
    db_cursor.execute("SELECT id from state where abbr = %s", city['state_abbr'])
    state_id = db_cursor.fetchone()
    db_cursor.execute("SELECT id from county where county = %s", city['county'])
    county_id = db_cursor.fetchone()
    if state_id and county_id:
        db_cursor.execute(insert_county_query , (city['place'], 
                                                city['postal_code'], 
                                                city['latitude'], 
                                                city['longitude'],
                                                state_id[0],
                                                county_id[0]))

db_conn.commit()
db_conn.close()