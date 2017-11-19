# Imports for flask
from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash

# Imports for sqlalchemmy and database classes
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

# Imports for creating anti-forgery token
from flask import session as login_session
import random
import string

# Imports for gconnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Load client id from json file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to Database and create database session
engine = create_engine('sqlite:///cataloginfo.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# JSON API endpoints to view Catalog Information
@app.route('/catalog/JSON')
def catalogJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


# JSON API endpoints to view Category Information
@app.route('/catalog/<string:category_name>/JSON')
def categoryJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_name=category_name).all()
    return jsonify(items=[i.serialize for i in items])


# JSON API endpoints to view Item Information
@app.route('/catalog/<string:category_name>/<string:item_name>/JSON')
def itemJSON(category_name, item_name):
    item = session.query(Item).filter_by(name=item_name).one()
    return jsonify(Item=item.serialize)


# Route for login page
@app.route('/login')
def showLogin():
    # Generate an Anti Forgery State Token to prevent cross site
    # request forgery
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    # return "Session %s" % login_session['state']
    return render_template('login.html', STATE=state)


# Route for creating a connection to google
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if the user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if the user exists, if not, create a new user ID
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += """ " style = "width: 250px;height: 250px;border-radius: 150px;
                -webkit-border-radius: 150px;-moz-border-radius: 150px;"> """
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# Helper functions for user ID and info
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Route for disconnecting from google
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        flash("Current user is not connected")
        return render_template('disconnect.html')
    print 'In gdisconnect access token is %s' % access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result

    # If disconnect is successfully delete user info from login session
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash("Successfully logged off")
        return render_template('disconnect.html')
    else:
        flash("Failed to revoke token for given user")
        return render_template('disconnect.html')


# Routes for root and showing catalog
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    recent_items = session.query(Item).order_by(Item.id.desc()).limit(10)
    return render_template('catalog.html', categories=categories,
                           recent_items=recent_items)


# Routes for showing category
@app.route('/catalog/<string:category_name>/')
@app.route('/catalog/<string:category_name>/items')
def showCategory(category_name):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_name=category.name).all()
    if 'username' not in login_session:
        return render_template('publiccategory.html', categories=categories,
                               category=category, items=items)
    else:
        return render_template('category.html', categories=categories,
                               category=category, items=items)


# Route for showing item
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def showItem(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(name=item_name).filter_by(
        category_name=category.name).first()
    creator = getUserInfo(item.user_id)
    if ('username' not in login_session or
            creator.id != login_session['user_id']):
        return render_template('publicitem.html', category=category, item=item)
    else:
        return render_template('item.html', category=category, item=item)


# Route for creating a new item
@app.route('/catalog/<string:category_name>/new/', methods=['GET', 'POST'])
def addItem(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['desc'],
                       imageurl=request.form['image'],
                       category_name=request.form['category'],
                       user_id=login_session['user_id'])

        # If the name already exists in the database, flash an error
        if session.query(Item).filter_by(name=newItem.name).filter_by(
                category_name=newItem.category_name).all():
            flash("""This item name already exists in that category.
                    Please try a different name.""")
            return render_template('newitem.html', categories=categories,
                                   category=category, item=newItem)
        else:
            session.add(newItem)
            session.commit()
            flash("Item \"%s\" was added to the %s category."
                  % (newItem.name, newItem.category_name))
            return redirect(url_for('showCategory',
                            category_name=newItem.category_name))
    else:
        return render_template('newitem.html', categories=categories,
                               category=category)


# Route for editing an item
@app.route('/catalog/<string:category_name>/<string:item_name>/edit',
           methods=['GET', 'POST'])
def editItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    editedItem = session.query(Item).filter_by(name=item_name).filter_by(
                 category_name=category.name).first()

    # Redirect user if they are not authorized to edit the item
    if editedItem.user_id != login_session['user_id']:
        flash("""You are not authorized to edit this item.  Please create
              your own item in order to edit it.""")
        return redirect(url_for('showItem', category_name=category_name,
                                item_name=item_name))
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['desc']:
                editedItem.description = request.form['desc']
        elif request.form['desc'] == "":
            editedItem.description = ""
        if request.form['image']:
            editedItem.imageurl = request.form['image']
        if request.form['category']:
            editedItem.category_name = request.form['category']

        # If there are multiple names in the database, flash an error
        if session.query(Item).filter_by(name=editedItem.name).filter_by(
                category_name=editedItem.category_name).count() > 1:
            flash("""This item name already exists in that category.
                    Please try a different name/category.""")
            return render_template('edititem.html', categories=categories,
                                   category=category, item=editedItem)
        else:
            session.add(editedItem)
            session.commit()
            if (category.name != editedItem.category_name):
                flash("""Item \"%s\" was successfully updated and moved to the
                      %s category."""
                      % (editedItem.name, editedItem.category_name))
            else:
                flash("""Item \"%s\" from the %s category was successfully
                      updated."""
                      % (editedItem.name, editedItem.category_name))
            return redirect(url_for('showItem',
                            category_name=editedItem.category_name,
                            item_name=editedItem.name))
    else:
        return render_template('edititem.html', categories=categories,
                               category=category, item=editedItem)


# Route for deleting an item
@app.route('/catalog/<string:category_name>/<string:item_name>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    itemToDelete = session.query(Item).filter_by(name=item_name).filter_by(
                   category_name=category.name).first()
    itemName = itemToDelete.name

    # Redirect user if they are not authorized to delete the item
    if itemToDelete.user_id != login_session['user_id']:
        flash("""You are not authorized to delete this item.  Please create
              your own item in order to delete.""")
        return redirect(url_for('showItem', category_name=category_name,
                                item_name=item_name))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Item \"%s\" was deleted." % itemName)
        return redirect(url_for('showCategory', category_name=category.name))
    else:
        return render_template('deleteitem.html', category=category,
                               item=itemToDelete)


if __name__ == '__main__':
    # Add secret key for flash messages
    app.secret_key = 'super_secret_key'
    # Reload server each time code changes for debugging
    app.debug = True
    # Run local server
    app.run(host='0.0.0.0', port=8000)
