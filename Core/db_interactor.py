#Database adapter
import psycopg2
import os
import pdb

DB_NAME =  os.environ['USER']
DB_HOST =  os.environ['localhost']
DB_PASS =  os.environ['PASSWORD']

#STATEMENTS
#
CREATE_TABLE = """CREATE TABLE PROJECTS( ID BIGSERIAL PRIMARY KEY  NOT NULL,
    CONTENT JSON  NOT NULL,
    OWNER INT[] NOT NULL,
    GROUP INT[]
    );"""
GET_ROW_BY_USER = "SELECT * FROM PROJECTS WHERE %s IN OWNER"
try:
    conn = psycopg2.connect("dbname='template1' user='%s' host='%s' password='%s'" % (DB_NAME, DB_HOST, DB_PASS))
except:
    print "I am unable to connect to the database"

cur = conn.cursor()

def executeStatement(executableStatement, arguments):
# helper method to execute a query and get responses
    cur.execute(executeStatement, arguments)
    rows = cur.fetchall()
    return rows

def getGraph(id):
    executeStatement(GET_ROW_BY_USER, (id))
    pdb.set_trace()
    pass
