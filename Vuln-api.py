from crypt import methods
import hashlib
import sqlite3
from flask import Flask,request,jsonify
import json


app = Flask(__name__)
db = "test.db"

def database_handler():
    return sqlite3.connect(db)

    
@app.route("/", methods=['GET'])
def main():
    message="AUTH API"
    return jsonify(message)

@app.route("/signup/v1",methods=["POST"])
def signup_v1():
    with database_handler() as connection:
        cur=connection.cursor()
        cur.execute(''' CREATE TABLE IF NOT EXISTS  USER_PLAIN
                        (USERNAME TEXT  PRIMARY KEY NOT NULL,
                        PASSWORD TEXT  NOT NULL);''')
        connection.commit()
        try:
            hashvalue=hashlib.sha256(request.form['password'].encode()).hexdigest()
            cur.execute("INSERT INTO USER_PLAIN (USERNAME,PASSWORD)"
                        "VALUES ('{0}', '{1}')".format(request.form['username'],hashvalue))
            connection.commit()
            message="signup success"
            return jsonify(message=message)
        except sqlite3.IntegrityError:
            message=f"username:{request.form['username']} has been already registerd."
            return jsonify(message=message)


def validate_creds(username,password):
    with database_handler() as connection:
        cur=connection.cursor()
        query="SELECT PASSWORD FROM USER_PLAIN WHERE USERNAME = '{0}'".format(username)
        cur.execute(query)
        records = cur.fetchone()
        if not records:
            return False
        return records[0] == hashlib.sha256(password.encode()).hexdigest()

@app.route("/login/v1",methods=["POST"])
def login_v1():
    try:
        if request.method == "POST":
            if validate_creds(request.form['username'],request.form['password']):
                error = "login success"
            else:
                error = "login fail" 
    except Exception as e:
            return jsonify({'error':str(e)})    
    return jsonify(error=error)

@app.route("/search/v1", methods=["GET"])
def search_v1():
    username= request.form['username']
    print(username)
    if request.method == "GET":
        with database_handler() as connection:
            cur=connection.cursor()
            query="SELECT * FROM USER_PLAIN WHERE USERNAME = '{0}'".format(username)
            cur.execute(query)
            records = cur.fetchall()
            return json.dumps(records)
        
            
if __name__ == "__main__":
        app.run(host="127.0.0.1",port="1234")


