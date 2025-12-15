from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    # return "Show all restaurants"
    db = sqlite3.connect('restaurant_menu.db') # local -> file name, 보통 네트워크 주소
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    items = cursor.execute(
        'select id, name from restaurant'
    ).fetchall()
    return render_template('restaurants.html', items=items)
    
    
    # output = ""
    # for item in items:
    #     output += f"{item['name']}"
    #     output += "<br>"
    # return output

@app.route('/restaurant/new/')
def newRestaurants():
    return "add a new restaurant"


#@app.route('/')
#@app.route('/hello/')
#@app.route('/hello/<string:name>/')
#def hello_web(name=None):
#    # return '<h1> Hello, Web App. </h1>' if name==None else f'<h1> Hello, {name}!</h1>'
#    return render_template('hello.html', name=name)

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000)

