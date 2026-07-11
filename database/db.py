import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",          # Change if you have a password
        database="airline_db"
    )