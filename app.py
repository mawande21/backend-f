from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
app.debug = True
CORS(app)

# configuration of mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'manjatilifechoices@gmail.com'
app.config['MAIL_PASSWORD'] = 'mawande99'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


def log_table():
    conn = sqlite3.connect('database.db')
    print('database has been opened')
    conn.execute('CREATE TABLE IF NOT EXISTS USERS (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, surname TEXT, email TEXT, password TEXT)')
    print('table was sucess')
    print(conn.execute("PRAGMA table_info('USERS')").fetchall())
    conn.close()


# making keys for database
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

log_table()


# logins for the host
@app.route('/add-host/', methods=['POST'])
def add_new_record():
    msg = []
    if request.method == "POST":
        try:
            post_data = request.get_json()
            name = post_data['name']
            surname = post_data['surname']
            email = post_data['email']
            password = post_data['password']

            if name == name:
                with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO USERS (name, surname, email, password) VALUES (?, ?, ?, ?)", (name, surname, email, password))
                    con.commit()
                    msg = name + " is the host of this chat."
                    send_mail(name, surname, email, password)
                    return jsonify(msg)
        except Exception as e:
            con.rollback()
            msg = "Error occurred in insert operation: " + str(e)

        finally:
            con.close()
        return jsonify(msg=msg)



# all the hosts results
@app.route('/show-results/', methods=["GET"])
def show_results():
    results = []
    try:
        with sqlite3.connect('database.db') as con:
            con.row_factory = dict_factory
            cur = con.cursor()
            cur.execute("SELECT * FROM USERS")
            results = cur.fetchall()
            print(results)
    except Exception as e:
        con.rollback()
        print("There was an error fetching results from the database: " + str(e))
    finally:
        con.close()
        return jsonify(results)

@app.route('/mail/')
def index():
    msg = Message(
        "Hello Json",
        sender='manjatilifechices@gmail.com',
        recipients=['manjatilifechoices@gmail.com']
    )
    msg.body = 'Hello Flask message sent from Flask-Mail'
    mail.send(msg)
    return 'Sent'


def send_mail(name, surname, email, password):
    msg = Message(
        "Confirmation of booking",
        sender=email,
        recipients=[email]
    )
    msg.body = """
        Dear {name} {surname},
        
        It is a pleasure having you on my chat app, hope you had a lot of fun.
        
        Your username and password for signing in are {name} and {password}.
        
        If there's any question you'll like to ask kindly reply on this email
        
        Thank you
        Mawande Manjati
    """.format(name=name, surname=surname, email=email, password=password)
    mail.send(msg)


if __name__ == "__main__":
    app.run(debug="true")
