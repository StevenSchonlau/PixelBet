import mysql.connector
from dotenv import load_dotenv
import os

###
# This contains the basic CRUD operations for the database. Look at CS407/Sprint 1/SQL Server to set it up
###


load_dotenv()

#vals to be set later
_cursor = None
_cnx = None

def connect_db():
    database = os.getenv("DATABASE")
    host = os.getenv("HOST")
    user = os.getenv("USER")
    db_password =os.getenv("DB_PASSWORD")

    global _cnx
    _cnx = mysql.connector.connect(user=user, password=db_password,
                                host=host,
                                database=database)
    global _cursor
    _cursor = _cnx.cursor()

def close_db():
    _cnx.commit()
    _cursor.close()
    _cnx.close()

#cols are for column names, vals are corresponding values
def create(cols, vals, table):
    connect_db()
    add_entry = "INSERT INTO " + table + " ("
    add_entry += ", ".join(cols)
    add_entry += ") VALUES ("
    add_entry += ", ".join(vals)
    try:
        _cursor.execute(add_entry)
        close_db()
        return True
    except:
        close_db()
        return False

#cols are for column names, vals are corresponding values. If none specified, will return whole table
def read(table, cols=[], vals=[]):
    connect_db()
    read_entry = "SELECT * FROM " + table 
    if len(cols) != 0:
        read_entry += " WHERE"
        combined_arr = []
        for c in range(0, len(cols)):
            combined_arr.append(cols[c] + "='" + vals[c] + "'")
        read_entry += " AND ".join(combined_arr)
    try:
        data = _cursor.execute(read_entry)
        close_db()
        return data
    except:
        close_db()
        return None

#updates entries with wcols/wvals criteria to cols/vals
def update(table, cols, vals, wcols, wvals):
    connect_db()
    update_entry = "UPDATE " + table + " SET "
    combined_set_arr = []
    for c in range(0, len(cols)):
        combined_set_arr.append(cols[c] + "='" + vals[c] + "'")
    update_entry += ", ".join(combined_set_arr)
    if len(wcols) != 0:
        update_entry += " WHERE"
        combined_arr = []
        for c in range(0, len(wcols)):
            combined_arr.append(wcols[c] + "='" + wvals[c] + "'")
        update_entry += " AND ".join(combined_arr)
    try:
        _cursor.execute(update_entry)
        close_db()
        return True
    except:
        close_db()
        return False


#deletes entries matching cols/vals
def delete(table, cols, vals):
    connect_db()
    delete_entry = "DELETE FROM " + table 
    if len(cols) != 0:
        delete_entry += " WHERE"
        combined_arr = []
        for c in range(0, len(cols)):
            combined_arr.append(cols[c] + "='" + vals[c] + "'")
        delete_entry += " AND ".join(combined_arr)
    try:
        _cursor.execute(delete_entry)
        close_db()
        return True
    except:
        close_db()
        return False


