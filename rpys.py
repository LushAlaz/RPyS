from flask import Flask, redirect, request, session, make_response, render_template
from flask_bcrypt import Bcrypt
from secrets import token_urlsafe
from html import escape
from os.path import isfile
import atexit
import csv

HOST = '0.0.0.0'

# dont wanna deal with a real database so csv will do lol
def get_leaderboard(filename):
    if not isfile(filename): return []

    with open(filename, "r", newline='') as file:
        reader = csv.DictReader(file, delimiter=',')

        leaderboard = [{"name": row["name"], "wins": int(row["wins"]), "session": row['session'], "password": row['password']} for row in reader]
        leaderboard.sort(reverse=True, key=lambda d:int(d["wins"])) # just in case
        return leaderboard

# used to check if any current users have the same of a certain value (like a name)
# its a one liner either way but the function is just easier to read
def checkifValueInUsers(key, value):
    return any([x[key] == value for x in wins_leaderboard])


app = Flask(__name__)
bcrypt = Bcrypt(app)


wins_leaderboard = get_leaderboard('leaderboard.csv')
print(wins_leaderboard)

@app.route('/')
def index():
    if request.cookies.get("session") == None:
       return redirect("/login")
    else:
       return redirect("/game")


@app.route('/game')
def game():
    if request.cookies.get("session") == None:
       return redirect("/login")
    return render_template("game.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    data = request.get_json()
    name = escape(data["name"])
    pw = escape(data["password"])
    if not checkifValueInUsers("name", name):
        return "No user with that name exists", 400
    
    account = [x for x in wins_leaderboard if x['name'] == name][0]
    
    pw_correct = bcrypt.check_password_hash(account['password'], pw)
    
    if not pw_correct:
        return "Username or Password is incorrect", 400
    
    
    res = make_response("Success", 200)
    res.set_cookie('session', account["session"], httponly=True) 

    return res

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
     
    data = request.get_json()
    name = escape(data["name"])
    pw = escape(data["password"])
    
    if checkifValueInUsers("name", name):
        return "Name is taken", 400
    
    session_id = token_urlsafe(16)
    res = make_response("Success", 200)
    res.set_cookie('session', session_id, httponly=True)    
    
    hashed_pw = bcrypt.generate_password_hash(escape(pw)).decode('utf8')
    # session_id is stored so people don't have to log in again if the server restarts
    wins_leaderboard.append({"name": name, "wins": 0, "session": session_id, "password": hashed_pw})
    # didnt wanna do this but insort_left is being bad
    wins_leaderboard.sort(reverse=True, key=lambda d:int(d["wins"]))

    return res

@app.route('/win', methods=["POST"])
def win():
    session_id = request.cookies.get("session")
    if not checkifValueInUsers("session", session_id):
        return "Unauthorized", 401
   
    entry = [i for i in wins_leaderboard if i["session"] == session_id]
    if len(entry) > 0:
        wins_leaderboard[wins_leaderboard.index(entry[0])]["wins"] += 1
        wins_leaderboard.sort(reverse=True, key=lambda d:int(d["wins"]))
        return str(wins_leaderboard[wins_leaderboard.index(entry[0])]["wins"]), 200
    else:
        return "The request had a name which is not on the leaderboard. Either request was malformed or name got deleted from leaderboard.", 400

@app.route('/logout')
def logout():
    res = make_response(render_template("logout.html"))
    res.delete_cookie("session")
    return res



@app.route('/wins')
def leaderboard():
    return render_template("leaderboard.html", wins=wins_leaderboard, length=len(wins_leaderboard), session=request.cookies.get('session'))


@atexit.register
def serialize_leaderboard():
    with open("leaderboard.csv", "w", newline='') as file:
        field_names = ['name', 'wins', 'session', 'password']
        writer = csv.DictWriter(file, fieldnames=field_names)

        writer.writeheader()
        for plr in wins_leaderboard:
            writer.writerow(plr)

if __name__ == '__main__':
    app.run(port=80, host=HOST)