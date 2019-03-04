#!/usr/bin/env python
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash, session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from database_setup import Base, Category, Item, User


import os
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


import hashlib
import uuid
salt = uuid.uuid4().hex


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

app = Flask(__name__)

engine = create_engine('sqlite:///productcatalog.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
dbsession = DBSession()

# Default endpoint that loads up the page


@app.route("/")
def index():
    category = dbsession.query(Category).all()
    items = dbsession.query(Item).all()
    return render_template("catalog.html", category=category, items=items)


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


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
    loginurl = ("https://www.googleapis.com/oauth2/v1"
                "/tokeninfo?access_token=")
    url = (loginurl+""
           ""+str(access_token))
    print(url)
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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is \
                   already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    try:
        login_session['username'] = data['name']
    except BaseException:
        login_session['username'] = 'No userName'
        data['name'] = 'No userName'

    try:
        login_session['picture'] = data['picture']
    except BaseException:
        login_session['picture'] = None
    login_session['email'] = data['email']
    user = dbsession.query(User).filter_by(email=data['email']).one_or_none()
    if user:
        print ('The user exists in the system')
        login_session['id'] = user.id
    else:
        user = User(user_name=data['name'], email=data['email'])
        dbsession.add(user)
        dbsession.commit()
        print('Added new user. user id ' + str(user.id))
        login_session['id'] = user.id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src = "'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: \
               150px;-webkit-border-radius: 150px;-moz-border-radius: \
               150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not \
                   connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token = %s'\
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to \
                 revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Endpoint that lists out the items for particular category
@app.route("/catalog/<cat_name>/items", methods=['GET', 'POST'])
def catalog_index(cat_name):
    categories = dbsession.query(Category).all()
    category = dbsession.query(Category).filter_by(name=cat_name).one()
    items = dbsession.query(Item).filter_by(cat_id=category.id).all()
    return (render_template("category_items.html", categories=categories,
                            items=items, category=category))


# Endpoint that shows description of particular item
@app.route("/catalog/<cat_name>/<item_name>", methods=['GET', 'POST'])
def item_description(cat_name, item_name):
    category = dbsession.query(Category).filter_by(name=cat_name).one()
    item = dbsession.query(Item).filter_by(title=item_name).one()
    if login_session:
        try:
            if login_session['id'] and login_session['id'] == item.user_id:
                login_session['editable'] = True
            else:
                login_session['editable'] = None
        except BaseException:
            login_session['editable'] = None
    else:
        login_session['editable'] = None
    return (
        render_template(
            "item_description.html",
            item=item,
            category=category))

# Endpoint that allows user to edit
@app.route("/catalog/<item_name>/edit", methods=['GET', 'POST'])
def edit_item(item_name):
    categories = dbsession.query(Category).all()
    item = dbsession.query(Item).filter_by(title=item_name).one()
    return render_template("editItem.html", item=item, categories=categories)


@app.route("/catalog/edit/<item_id>", methods=['GET', 'POST'])
def edit_existing_item(item_id):
    editedItem = dbsession.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        else:
            flash('Title cannot be empty.\
                   Please provide proper information item.')
            categories = dbsession.query(Category).all()
            item = dbsession.query(Item).filter_by(id=item_id).one()
            return (render_template("editItem.html",
                                    item=item, categories=categories))

        if request.form['description']:
            editedItem.description = request.form['description']
        else:
            flash('Description cannot be empty. \
              Please provide proper information item.')
            categories = dbsession.query(Category).all()
            item = dbsession.query(Item).filter_by(id=item_id).one()
            return render_template(
                "editItem.html",
                item=item,
                categories=categories)
        cat_name = request.form['category']
        category = dbsession.query(Category).filter_by(name=cat_name).one()
        editedItem.cat_id = category.id
        dbsession.add(editedItem)
        dbsession.commit()

    category = dbsession.query(Category).filter_by(name=cat_name).one()
    item = dbsession.query(Item).filter_by(id=item_id).one()
    return (render_template("item_description.html",
                            item=item, category=category))


@app.route("/catalog/add", methods=['GET', 'POST'])
def add_item():
    categories = dbsession.query(Category).all()
    return render_template("addItem.html", categories=categories)


@app.route("/catalog/addNewItem", methods=['GET', 'POST'])
def add_new_item():
    if request.method == 'POST':
        new_item = Item()
        if request.form['title']:
            new_item.title = request.form['title']
        else:
            flash('Title cannot be empty. Please provide \
                proper information item.')
            categories = dbsession.query(Category).all()
            return render_template("addItem.html", categories=categories)
        if request.form['description']:
            new_item.description = request.form['description']
        else:
            flash('Description cannot be empty. \
                Please provide proper information item.')
            categories = dbsession.query(Category).all()
            return render_template("addItem.html", categories=categories)
        cat_name = request.form['category']
        category = dbsession.query(Category).filter_by(name=cat_name).one()
        new_item.cat_id = category.id
        new_item.user_id = login_session['id']
        dbsession.add(new_item)
        dbsession.commit()

    category = dbsession.query(Category).all()
    items = dbsession.query(Item).all()
    return render_template("catalog.html", category=category, items=items)


@app.route("/catalog/<item_name>/delete", methods=['GET', 'POST'])
def delete_item(item_name):
    item = dbsession.query(Item).filter_by(title=item_name).one()
    return render_template("deleteItem.html", item=item)


@app.route("/catalog/delete/<item_id>", methods=['GET', 'POST'])
def delete_item_from_db(item_id):
    itemToDelete = dbsession.query(Item).filter_by(id=item_id).one()
    dbsession.delete(itemToDelete)
    dbsession.commit()
    category = dbsession.query(Category).all()
    items = dbsession.query(Item).all()
    return render_template("catalog.html", category=category, items=items)


@app.route("/catalog/login", methods=['GET', 'POST'])
def catalog_login():
    state = (''.join(random.choice(
             string.ascii_uppercase + string.digits)
        for x in xrange(32)))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route("/catalog/logout", methods=['GET', 'POST'])
def catalog_logout():
    login_session.pop('state', None)
    login_session.pop('editable', None)
    category = dbsession.query(Category).all()
    items = dbsession.query(Item).all()
    return render_template("catalog.html", category=category, items=items)


@app.route('/catalog.json')
def catalogJSON():
    categories = (dbsession.query(Category).
                  options(joinedload(Category.items)).all())
    json_ob = (dict(category=[dict(c.serialize,
                                   items=[i.serialize for i in c.items])
                              for c in categories]))
    return jsonify(json_ob)


@app.route('/category/<int:cat_id>/item/JSON')
def catalogCategoryJSON(cat_id):
    category = dbsession.query(Category).filter_by(id=cat_id).one_or_none()
    items = dbsession.query(Item).filter_by(cat_id=cat_id).all()
    if category:
        json_ob = dict(category=[dict(category.serialize,
                                      items=[i.serialize for i in items])])
    else:
        json_ob = dict(category=None)
    return jsonify(json_ob)


@app.route('/category/<int:cat_id>/item/<int:item_id>/JSON')
def catalogCategoryItemJSON(cat_id, item_id):
    category = dbsession.query(Category).filter_by(id=cat_id).one_or_none()
    item = dbsession.query(Item).filter_by(
        cat_id=cat_id, id=item_id).one_or_none()

    if category and item:
        json_ob = dict(category=[dict(category.serialize,
                                      item=[item.serialize])])
    elif category:
        json_ob = dict(category=[dict(category.serialize,
                                      item=None)])
    else:
        json_ob = dict(category=None)
    return jsonify(json_ob)


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
