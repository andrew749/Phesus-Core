#Database adapter
import psycopg2
import os
import json
import pdb
import numpy as np
from psycopg2.pool import ThreadedConnectionPool

DB_NAME =  'phesus'
DB_USER = 'dummy'
DB_PASS = 'dummy'
DB_HOST = 'localhost'

DEBUG=True

class NodeType:
    """An enumeration of the different types of nodes."""
    NORMAL = "normal"
    DIAMOND = "diamond"

class ConnectionType:
    """An enumeration of the different types of connections."""
    NORMAL = "normal"
    BIDIRECTIONAL = "bi"

class PermissionType:
    """An enumeration of the different types of access to a project."""
    READ = 1
    WRITE = 2
    READWRITE = 3


#STATEMENTS
CREATE_NODES_TABLE = """
    CREATE TABLE IF NOT EXISTS NODES (
    ID SERIAL PRIMARY KEY  NOT NULL,
    X INT NOT NULL,
    Y INT NOT NULL,
    TYPE TEXT NOT NULL,
    CONTENT JSON  NOT NULL,
    PROJECT SERIAL NOT NULL REFERENCES PROJECTS(ID)
    );
"""
CREATE_CONNECTION_TABLE = """
    CREATE TABLE IF NOT EXISTS CONNECTIONS (
    ID SERIAL PRIMARY KEY  NOT NULL,
    PROJECT SERIAL NOT NULL REFERENCES PROJECTS(ID),
    TYPE TEXT NOT NULL,
    FROMNODE INT NOT NULL,
    TONODE INT NOT NULL,
    METADATA JSON
    );
"""
CREATE_USERS_TABLE = """
    CREATE TABLE IF NOT EXISTS USERS (
    NAME TEXT,
    EMAIL TEXT,
    GOOGLE_ID TEXT PRIMARY KEY NOT NULL
    );
"""
CREATE_PROJECTS_TABLE = """
    CREATE TABLE IF NOT EXISTS PROJECTS (
    ID SERIAL PRIMARY KEY NOT NULL,
    OWNER TEXT NOT NULL,
    MEMBERS TEXT[]
    );
"""
GET_NODES_BY_PROJECT  = """
    SELECT ID, X, Y, TYPE, CONTENT  FROM NODES WHERE PROJECT=%s;
 """

GET_CONNECTIONS_BY_PROJECT = """
    SELECT ID, TYPE, FROMNODE, TONODE, METADATA FROM CONNECTIONS WHERE PROJECT=%s;
"""
VERIFY_USER_IS_PART_OF_PROJECT = """
    SELECT EXISTS (
    SELECT * FROM PROJECTS WHERE %s in OWNER || MEMBERS;
    );
"""
#first param is nodeid second is the porjet id
VERIFY_NODE_IS_IN_PROJECT = """
    SELECT EXISTS(
    SELECT * FROM NODES WHERE %s=ID AND %s=PROJECT;
    );
"""
CREATE_USER = """INSERT INTO USERS (NAME, EMAIL, GOOGLE_ID) VALUES (%s, %s, %s) ON CONFLICT (GOOGLE_ID) DO NOTHING;"""
CREATE_GRAPH = """INSERT INTO PROJECTS (OWNER, MEMBERS) VALUES (%s, %s) RETURNING ID;"""
CREATE_NODE = """INSERT INTO NODES (X,Y,TYPE,CONTENT,PROJECT) VALUES (%s, %s, %s, %s, %s) RETURNING ID;"""
CREATE_CONNECTION = """INSERT INTO CONNECTIONS (PROJECT, TYPE, FROMNODE, TONODE, METADATA) VALUES (%s, %s, %s, %s, %s) RETURNING ID;"""
UPDATE_NODE = """UPDATE NODES SET x = %s, y = %s, type = %s, content = %s,   where ID = %s;"""
UPDATE_CONNECTION = """UPDATE CONNECTIONS SET type = %s, tonode = %s, fromnode = %s, metadata = %s where ID = %s;"""
DELETE_NODE = """DELETE FROM NODES WHERE %s=ID; DELETE FROM CONNECTIONS WHERE %s in FROMNODE || TONODE;""" #both params are node id, when you delete a node all refs are invalid
DELETE_CONNECTION = """DELETE FROM CONNECTIONS WHERE %s = ID; """
CHECK_IF_NODE_IS_IN_PROJECT = """
SELECT EXISTS (
    SELECT * FROM NODES WHERE ID = %s AND project = %s
    );
"""
CHECK_IF_CONNECTION_IS_IN_PROJECT = """
SELECT EXISTS (
    SELECT * FROM CONNECTIONS WHERE ID = %s AND project = %s
    );
"""
CHECK_IF_USER_IS_IN_PROJECT = """
SELECT EXISTS (
    SELECT * FROM PROJECTS WHERE %s = ID AND %s = OWNER
    );
"""
CHECK_IF_USER_EXISTS = """
SELECT EXISTS(
    SELECT * FROM USERS WHERE %s = GOOGLE_ID
);
"""
# GET_PROJECTS = """
# SELECT ID FROM PROJECTS WHERE %s=OWNER OR %s=ANY(MEMBERS);
# """
GET_PROJECTS = """
SELECT ID FROM PROJECTS WHERE %s=OWNER;
"""
pool = ThreadedConnectionPool(1, 10, "dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME,DB_USER, DB_HOST, DB_PASS))

def initTables():
    """ Initializes tables if they dont already exist."""
    executeStatement(CREATE_PROJECTS_TABLE, None, False)
    executeStatement(CREATE_NODES_TABLE, None, False)
    executeStatement(CREATE_USERS_TABLE, None, False)
    executeStatement(CREATE_CONNECTION_TABLE, None, False)

def executeStatement(executableStatement, arguments, getResult):
    """
    Helper method to execute a query and get responses.
    :param executableStatement: A string of the database query to perform.
    :param arguments: A tuple of the arguments to insert into the executable statement.
    :param getResult: Boolean representing whether or not to return something at the end of the query.
    :return returns the query if specified in getResult
    """
    conn = pool.getconn()
    if (conn is None):
        return None

    cur = conn.cursor()

    cur.mogrify(executableStatement, arguments)
    if (arguments is not None):
        cur.execute(executableStatement, arguments)
    else:
        cur.execute(executableStatement)
    conn.commit()
    pool.putconn(conn)
    if getResult:
        rows = cur.fetchall()
        return rows

def checkIfUserExists(uid):
    return executeStatement(CHECK_IF_USER_EXISTS, (uid,), True)

""" Helper functions that decorate other functions,
    can check authentication and read and write
    permissions here.
"""
def CanRead(func):
    """Decorator to wrap functions and restrict access if a user can't read"""
    def i(*args, **kwargs):
        if(checkIfUserExists(kwargs['uid']) and verifyUserCanRead(kwargs['uid'], kwargs['pid'])):
            return func(*args, **kwargs)
        else:
            return json.dumps({"ERROR":"Cannot Read"})
    return i

def CanWrite(func):
    """Same as read but with write permissions"""
    def i(*args, **kwargs):
        if(checkIfUserExists(kwargs['uid']) and verifyUserCanEdit(kwargs['uid'], kwargs['pid'])):
            return func(*args, **kwargs)
        else:
            return json.dumps({"ERROR":"Cannot Write"})
    return i

"""Remaining helper functions to access the db"""

@CanRead
def getNodesByProject(uid,
                      pid):
    """
    Return an array of nodes for the project.
    :param uid: The id of the user to access the project.
    :param pid: The id of the project to get the nodes for.
    :return Rows each representing a node of the project.
    """
    data = executeStatement(GET_NODES_BY_PROJECT,  (pid,), True)
    # columns = ('id','x', 'y','type', 'content')
    results = {}
    dict_from_row = lambda x: {'x':x[1], 'y':x[2], 'type':x[3], 'content':x[4]}
    for row in data:
        results[row[0]] = dict_from_row(row)
    return results

@CanRead
def getConnectionsByProject(uid,
                            pid):
    """
    Return all the edges of the graph.
    :param uid: Id
    :param pid: Project Id
    """
    data = executeStatement(GET_CONNECTIONS_BY_PROJECT, (pid,), True)
    # columns = ('id', 'type', 'fromnode', 'tonode', 'metadata')
    results = {}
    dict_from_row = lambda x: {'type':x[1], 'from':str(x[2]), 'to':str(x[3]), 'metadata': x[4]}
    for row in data:
        results[row[0]] = dict_from_row(row)
    return results

@CanRead
def getProject(uid,
               pid):
    """
    Helper returns the json object of the graph.
    :param uid: The unique userId.
    :param pid: The unique id of the project to get.
    :return A dictionary containing the nodes and connections of the project.
    """
    nodes = getNodesByProject(uid=uid, pid=pid)
    connections = getConnectionsByProject(uid=uid, pid=pid)
    return json.dumps({"pid":pid,"nodes":nodes, "connections":connections})

def getProjects(uid=None):
    data = np.array(executeStatement(GET_PROJECTS,(uid,), True))
    return json.dumps(data[:,0].tolist())

#Anyone can create a graph
def createProject(owner,
                  members):
    """
    Helper to create a graph.
    :param owner:userid to own the graph.
    :param members: Array of userId's who are associated with the graph.
    :return The new project id.
    """
    return executeStatement(CREATE_GRAPH, (owner, members), True)[0][0]

def createUser(name,
               email,
               gid):
    """
    A helper to create a user.
    :param name:The name of the user.
    :return The id of the newly created user.
    """
    executeStatement(CREATE_USER, (name, email, gid), False)

@CanWrite
def createNode(uid,
               pid,
               x,
               y,
               type,
               contentJson):
    """
    A helper to create a node.
    :param x: The x coordinate of the node.
    :param y: The y coordinate of the node.
    :param type: The type of the node to create. See NodeTypes.
    :param contentJson: The content for the node.
    :param pid: The project that the node is associated with.
    :return The node id of the newly created node.
    """
    return executeStatement(CREATE_NODE, (x, y, type, contentJson, pid), True)

@CanWrite
def createConnection(uid,
                     pid,
                     type,
                     fromnode,
                     tonode,
                     metadata):
    """
    A helper to create a connection.
    :param pid: The id of the project associated with the node.
    :param type: The type of connection.
    :param fromnode: The id of the origin node.
    :param tonode: The id of the destination node.
    :param metadata: Json formatted metadata associated with the connection.
    :return The id of the created connection.
    """
    return executeStatement(CREATE_CONNECTION, (pid, type, fromnode, tonode, metadata), True)[0][0]

@CanWrite
def deleteNode(uid, pid, nodeId):
    """
    Helper to delete a node.
    :param nodeId: Id of the node to delete.
    """
    executeStatement(DELETE_NODE, (nodeId, nodeId), False)

@CanWrite
def deleteConnection(uid, pid, connectionId):
    """
    Helper to delete a connection.
    :param connectionId: Id of the connection to delete.
    """
    executeStatement(DELETE_CONNECTION, (connectionId), False)

@CanWrite
def updateConnection(uid,
                     pid,
                     connectionId,
                     type,
                     fromnode,
                     tonode,
                     metadata):
    executeStatement(UPDATE_CONNECTION, (type, tonode, fromnode, metadata, connectionId), False)

@CanWrite
def updateNode(uid,
               pid,
               nodeId,
               x,
               y,
               type,
               content):
    #updates all fields
    executeStatement(UPDATE_NODE, (x, y, type, content, nodeId),False)

def checkIfNodeIsInProject(uid,
                           pid,
                           nodeId):
    """returns a boolean if a node is in a project"""
    return executeStatement(CHECK_IF_NODE_IS_IN_PROJECT, (nodeId, pid), True)

def checkIfConnectionIsInProject(uid,
                                 pid,
                                 connectionId):
    """returns a boolean if a connection is in a project"""
    return executeStatement(CHECK_IF_CONNECTION_IS_IN_PROJECT, (connectionId, pid),True)

def checkPermissionsNode(uid,
                         pid,
                         nodeId):
    """checks if a node is in the project"""
    return checkIfNodeIsInProject(uid, pid, nodeId)

def checkPermissionsConnection(uid,
                               pid,
                               connectionId):
    """checks if a connection is in the project"""
    #checks the permissions for a conncetion
    return checkIfConnectionIsInProject(uid=uid, pid=pid, connectionId=connectionId)

def checkIfUserIsInProject(uid,
                           pid):
    """
    Returns a boolean if the user is in a project.
    """
    return executeStatement(CHECK_IF_USER_IS_IN_PROJECT, (pid, uid), True)

def verifyUserCanRead(uid,
                      pid):
    """
    Return boolean if the user can ready.
    """
    return checkIfUserIsInProject(uid, pid)

def verifyUserCanEdit(uid,
                      pid):
    """
    Verify is a user has read permissions on a graph
    """
    return checkIfUserIsInProject(uid, pid)

#will create the tables if they don't exist
initTables()
