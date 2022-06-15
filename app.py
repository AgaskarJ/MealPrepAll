from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Identity 
from bs4 import BeautifulSoup
import requests



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db18.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db1 = SQLAlchemy(app)
ingredient_list = {}
price_list = {}
id_count = 1
#carbs_inc, protein_inc, fat_inc = 1

class Meals(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True) #unique id for every meal 
    title = db1.Column(db1.String(100)) 
    complete = db1.Column(db1.Boolean)
    ingredients = db1.Column(db1.String(100))
    prices = db1.Column(db1.String(100))
    carbs = db1.Column(db1.Float)
    protein = db1.Column(db1.Float)
    fat = db1.Column(db1.Float)
    #testing = db.Column(db.String(100))

@app.route('/')
def index():

    #show all Meals
    meal_list = Meals.query.all()
    
    temp = []
    for meal in meal_list:
        temp.append({'meal': meal, 'ing':ingredient_list[meal.ingredients],'prices':price_list[meal.prices], 'carbs': meal.carbs, 'protein': meal.protein, 'fat': meal.fat})
    return render_template('index1.html', temp=temp) #meal_list=meal_list)
    

@app.route('/add', methods=["POST"])
def add():
    global id_count
    #adds new meals
    #redirects and refreshes url page 
    url = request.form.get("url")
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    title = soup.title.string

    # ingredients: []
    # price: []

    meal_data = []
    for name in soup.find_all('li', {'class': 'wprm-recipe-ingredient'}):
        amt = name.find('span', {'class': 'wprm-recipe-ingredient-amount'}).get_text()
        #unit = name.find('span', {'class': 'wprm-recipe-ingredient-unit'}).get_text()
        names = name.find('span', {'class': 'wprm-recipe-ingredient-name'}).get_text()
        final_name = ' '.join((amt, names))
        meal_data.append(final_name)
    
    price_data = []
    for price in soup.find_all('li', {'class': 'wprm-recipe-ingredient'}):
     prices = price.find('span', {'class': 'wprm-recipe-ingredient-notes wprm-recipe-ingredient-notes-normal'}).get_text()
     price_data.append(prices)

    #do the way i did for title =...
    for num in soup.find_all("span", {"class": "wprm-nutrition-label-text-nutrition-container wprm-nutrition-label-text-nutrition-container-carbohydrates"}):
        amt = num.find("span", {"class": "wprm-nutrition-label-text-nutrition-value"}).text
        carbs_inc = amt #((float(amt)*3*4)/2000)*100

    for num in soup.find_all("span", {"class": "wprm-nutrition-label-text-nutrition-container wprm-nutrition-label-text-nutrition-container-protein"}):
        amt = num.find("span", {"class": "wprm-nutrition-label-text-nutrition-value"}).text
        protein_inc = amt #((float(amt)*3*4)/2000)*100

    for num in soup.find_all("span", {"class": "wprm-nutrition-label-text-nutrition-container wprm-nutrition-label-text-nutrition-container-fat"}):
        amt = num.find("span", {"class": "wprm-nutrition-label-text-nutrition-value"}).text
        fat_inc = amt #((float(amt)*3*9)/2000)*100
 
    test_str = "testing" + str(id_count)
    ingredient_list[test_str] = meal_data
    price_list[test_str] = price_data
    id_count += 1

    
    new_meal = Meals(title=title, complete = False, ingredients=test_str, prices=test_str, carbs=carbs_inc, protein=protein_inc, fat=fat_inc)
    db1.session.add(new_meal)
    db1.session.commit()
    return redirect(url_for("index"))

@app.route('/update/<int:meal_id>')
def update(meal_id):
    #updates meal status
    #query db for meal id and modify complete column
    meal = Meals.query.filter_by(id=meal_id).first()
    meal.complete = not meal.complete
    db1.session.commit()
    return redirect(url_for("index"))

@app.route('/delete/<int:meal_id>')
def delete(meal_id):
    #updates meal status
    #query db for meal id and modify complete column
    meal = Meals.query.filter_by(id=meal_id).first()
    db1.session.delete(meal)
    db1.session.commit()
    return redirect(url_for("index"))

if __name__ == '__main__':
    db1.create_all()
    app.run(debug=True)