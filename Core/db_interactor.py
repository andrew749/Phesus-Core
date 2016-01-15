#Database adapter
import psycopg2
import os
import pdb

DB_NAME =  os.environ['USER']
DB_HOST =  os.environ['localhost']
DB_PASS =  os.environ['PASSWORD']

#STATEMENTS

CREATE_NODES_TABLE = """
    CREATE TABLE NODES (ID BIGSERIAL PRIMARY KEY  NOT NULL,
    X_COORDINATE INT NOT NULL,
    Y_COORDINATE INT NOT NULL,
    TYPE TEXT NOT NULL,
    CONTENT JSON  NOT NULL,
    CONNECTIONS INT[],
    PROJECT INT NOT NULL
    );"""
CREATE_CONNECTION_TABLE = """
CREATE TABLE CONNECTIONS (
    ID BIGSERIAL PRIMARY KEY  NOT NULL,
    PROJECT INT NOT NULL,
    TYPE TEXT NOT NULL,
    FROM INT NOT NULL,
    TO INT NOT NULL,
    METADATA JSON
);
"""
CREATE_USERS_TABLE    = """CREATE TABLE USERS (ID BIGSERIAL PRIMARY KEY NOT NULL, GOOGLEID TEXT NOT NULL, NAME TEXT)"""
CREATE_PROJECTS_TABLE = """CREATE TABLE PROJECTS (ID BIGSERIAL PRIMARY KEY NOT NULL, OWNERS INT[] NOT NULL, GROUP INT[])"""
GET_ROW_BY_USER       = """SELECT * FROM PROJECTS WHERE %s IN OWNER"""
CREATE_GRAPH          = """INSERT INTO PROJECTS (CONTENT, OWNER, GROUP)"""
INSERT_NODE           = """INSERT INTO"""
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
#helper returns the json object of the graph
    executeStatement(GET_ROW_BY_USER, (id))
    pdb.set_trace()
    pass

def makeGraph():
#helper inserts an entry in the table

    pass
