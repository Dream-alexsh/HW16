import json
from datetime import datetime

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(100))


class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Offer(db.Model):
    __tablename__ = 'offer'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))


db.create_all()

with open('users.json', 'r', encoding='utf-8') as file:
    users = json.load(file)

users_list = []
for user in users:
    users_list.append(User(id=user['id'],
                           first_name=user['first_name'],
                           last_name=user['last_name'],
                           age=user['age'],
                           email=user['email'],
                           role=user['role'],
                           phone=user['phone']))

with db.session.begin():
    db.session.add_all(users_list)


with open('orders.json', 'r', encoding='utf-8') as file:
    orders = json.load(file)

orders_list = []
for order in orders:
    orders_list.append(Order(id=order['id'],
                             name=order['name'],
                             description=order['description'],
                             start_date=datetime.strptime(order['start_date'], '%m/%d/%Y'),
                             end_date=datetime.strptime(order['end_date'], '%m/%d/%Y'),
                             address=order['address'],
                             price=order['price'],
                             customer_id=order['customer_id'],
                             executor_id=order['executor_id'])
                       )
with db.session.begin():
    db.session.add_all(orders_list)


with open('offers.json', 'r', encoding='utf-8') as file:
    offers = json.load(file)

offers_list = []
for offer in offers:
    offers_list.append(Offer(id=offer['id'],
                             order_id=offer['order_id'],
                             executor_id=offer['executor_id'])
                       )

with db.session.begin():
    db.session.add_all(offers_list)


@app.route('/users')
def all_users():
    data = User.query.all()
    user_response = []

    for user in data:
        user_response.append({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'age': user.age,
            'email': user.email,
            'role': user.role,
            'phone': user.phone,
        })
    return jsonify(user_response)


@app.route('/users/<int:id>')
def user_id(id):
    user_id = User.query.get(id)
    return jsonify({
        "id": user_id.id,
        "first_name": user_id.first_name
    })


@app.route('/orders')
def all_orders():
    data = Order.query.all()
    order_response = []

    for order in data:
        order_response.append({
            'id': order.id,
            'name': order.name,
            'description': order.description,
            'start_date': order.start_date,
            'end_date': order.end_date,
            'address': order.address,
            'price': order.price,
            'customer_id': order.customer_id,
            'executor_id': order.executor_id,
        })
    return jsonify(order_response)


@app.route('/orders/<int:id>')
def order_id(id):
    order_id = Order.query.get(id)
    return jsonify({
        "id": order_id.id,
        "name": order_id.name
    })


@app.route('/offers')
def all_offers():
    data = Offer.query.all()
    offer_response = []

    for offer in data:
        offer_response.append({
            'id': offer.id,
            'order_id': offer.order_id,
            'executor_id': offer.executor_id,
        })
    return jsonify(offer_response)


@app.route('/offers/<int:id>')
def offer_id(id):
    offer_id = Offer.query.get(id)
    return jsonify({
        "id": offer_id.id,
        "order_id": offer_id.order_id,
        'executor_id': offer_id.executor_id,
    })


@app.route('/users', methods=['POST'])
def all_users_post():
    data = request.get_json()
    new_user = User(id=data['id'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    age=data['age'],
                    email=data['email'],
                    role=data['role'],
                    phone=data['phone'])

    db.session.add(new_user)
    db.session.commit()

    return '', 201


@app.route('/users/<int:id>', methods=['PUT','DELETE'])
def user_put_delete(id):
    if request.method == 'PUT':
        data = request.get_json()
        user = User.query.get(id)
        user.id = data['id']
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.age = data['age']
        user.email = data['email']
        user.role = data['role']
        user.phone = data['phone']

        db.session.add(user)
        db.session.commit()

        return '', 203

    elif request.method == 'DELETE':
        data = User.query.get(id)
        db.session.delete(data)
        db.session.commit()

        return '', 203


@app.route('/orders', methods=['POST'])
def all_orders_post():
    data = request.get_json()
    new_order = Order(id=data['id'],
                      name=data['name'],
                      description=data['description'],
                      start_date=datetime.strptime(data['start_date'], '%m/%d/%Y'),
                      end_date=datetime.strptime(data['end_date'], '%m/%d/%Y'),
                      address=data['address'],
                      price=data['price'],
                      customer_id=data['customer_id'],
                      executor_id=data['executor_id'])

    db.session.add(new_order)
    db.session.commit()

    return '', 201


@app.route('/offers', methods=['POST'])
def all_offers_post():
    data = request.get_json()
    new_offer = Offer(id=data['id'],
                      order_id=data['order_id'],
                      executor_id=data['executor_id'])

    db.session.add(new_offer)
    db.session.commit()

    return '', 201


@app.route('/orders/<int:id>', methods=['PUT','DELETE'])
def order_put_delete(id):
    if request.method == 'PUT':
        data = request.get_json()
        order = Order.query.get(id)
        order.name = data['name']
        order.description = data['description']
        order.start_date = datetime.strptime(data['start_date'], '%m/%d/%Y')
        order.end_date = datetime.strptime(data['end_date'], '%m/%d/%Y')
        order.address = data['address']
        order.price = data['price']
        order.customer_id = data['customer_id']
        order.executor_id = data['executor_id']

        db.session.add(order)
        db.session.commit()

        return '', 203

    elif request.method == 'DELETE':
        data = Order.query.get(id)
        db.session.delete(data)
        db.session.commit()

        return '', 203


@app.route('/offers/<int:id>', methods=['PUT','DELETE'])
def offer_put_delete(id):
    if request.method == 'PUT':
        data = request.get_json()
        offer = Offer.query.get(id)
        offer.order_id = data['order_id']
        offer.executor_id = data['executor_id']

        db.session.add(offer)
        db.session.commit()

        return '', 203

    elif request.method == 'DELETE':
        data = Offer.query.get(id)
        db.session.delete(data)
        db.session.commit()

        return '', 203


if __name__ == "__main__":
    app.run()


