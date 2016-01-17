#Database adapter
import psycopg2
import os
import pdb

DB_NAME =  'phesus'
DB_USER = 'dummy'
DB_PASS = 'dummy'
DB_HOST = 'localhost'

#STATEMENTS

CREATE_NODES_TABLE = """
    CREATE TABLE IF NOT EXISTS NODES (ID BIGSERIAL PRIMARY KEY  NOT NULL,
    X INT NOT NULL,
    Y INT NOT NULL,
    TYPE TEXT NOT NULL,
    CONTENT JSON  NOT NULL,
    PROJECT INT NOT NULL REFERENCES PROJECTS(ID)
    );"""

CREATE_CONNECTION_TABLE = """
    CREATE TABLE IF NOT EXISTS CONNECTIONS (
    ID BIGSERIAL PRIMARY KEY  NOT NULL,
    PROJECT INT NOT NULL REFERENCES PROJECTS(ID),
    TYPE TEXT NOT NULL,
    FROMNODE INT NOT NULL,
    TONODE INT NOT NULL,
    METADATA JSON
    );
"""

CREATE_USERS_TABLE    = """
    CREATE TABLE IF NOT EXISTS USERS (ID BIGSERIAL PRIMARY KEY NOT NULL,
    GOOGLEID TEXT NOT NULL,
    NAME TEXT
    );"""

CREATE_PROJECTS_TABLE = """
    CREATE TABLE IF NOT EXISTS PROJECTS (ID BIGSERIAL PRIMARY KEY NOT NULL,
    OWNERS INT[] NOT NULL,
    MEMBERS INT[]
    );"""

GET_NODES_BY_PROJECT  = """
    SELECT * FROM NODES WHERE PROJECT=%s;
"""

GET_CONNECTIONS_BY_PROJECT = """
    SELECT * FROM CONNECTIONS WHERE PROJECT=%s;
"""

VERIFY_USER_IS_PART_OF_PROJECT = """
    SELECT EXISTS (
    SELECT * FROM PROJECTS WHERE %s in OWNERS || MEMBERS;
    );
"""
#first param is nodeid second is the porjet id
VERIFY_NODE_IS_IN_PROJECT = """
    SELECT EXISTS(
    SELECT * FROM NODES WHERE %s=ID AND %s=PROJECT;
    );
"""

CREATE_GRAPH          = """INSERT INTO PROJECTS (OWNERS, MEMBERS) VALUES (%s, %s);"""

INSERT_NODE           = """INSERT INTO NODES (X,Y,TYPE,CONTENT,PROJECTS) VALUES (%s, %s, %s, %s, %s);"""

INSERT_CONNECTION = """INSERT INTO CONNECTIONS (PROJECT, TYPE, FROMNODE, TONODE, METADATA) VALUES (%s, %s, %s, %s, %s);"""

#both params are node id
DELETE_CONNECTION = """DELETE FROM NODES WHERE %s=ID; DELETE FROM CONNECTIONS WHERE %s in FROMNODE || TONODE;"""

try:
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME,DB_USER, DB_HOST, DB_PASS))
    cur = conn.cursor()
except:
    print ("I am unable to connect to the database")


def initTables():
    executeStatement(CREATE_PROJECTS_TABLE, None, False)
    executeStatement(CREATE_NODES_TABLE, None, False)
    executeStatement(CREATE_USERS_TABLE, None, False)
    executeStatement(CREATE_CONNECTION_TABLE, None, False)

def executeStatement(executableStatement, arguments, getResult):
# helper method to execute a query and get responses
    if (arguments is not None):
        cur.execute(executableStatement, arguments)
    else:
        cur.execute(executableStatement)
    conn.commit()
    if getResult:
        rows = cur.fetchall()
        return rows

def getGraph(userId, projectId):
#helper returns the json object of the graph
    if(verifyUserCanRead(userId, projectId)):
        nodes = getNodesByProject(userId, projectId)
        connections = getConnectionsByProject(userId, projectId)
        pdb.set_trace()
    else:
        return None

def getNodesByProject(userId, projectId):
    #return an array of nodes for the project
    return executeStatement(GET_NODES_BY_PROJECT,  (projectId), True)

def getConnectionsByProject(userId, projectId):
    #return all the edges of the graph
    return executeStatement(GET_CONNECTIONS_BY_PROJECT, (projectId), True)

def createGraph(userId):
    executeStatement(CREATE_GRAPH, (userId, (None)))
    pass

#TODO work on permissions
def verifyUserCanRead(userId, projectId):
    #return boolean if the user can ready
    return True

def verifyUserCanEdit(userId, projectId):
    #verify is a user has read permissions on a graph
    return True


#START OF PROGRAM
initTables()
