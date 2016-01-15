#Database adapter
import psycopg2
import os

DB_NAME =  os.environ['USER']
DB_HOST =  os.environ['localhost']
DB_PASS =  os.environ['PASSWORD']
try:
    conn = psycopg2.connect("dbname='template1' user='%s' host='%s' password='%s'")
except:
    print "I am unable to connect to the database"
