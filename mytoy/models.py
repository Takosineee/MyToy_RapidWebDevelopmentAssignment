from . import db

class Series(db.Model):
    __tablename__ = 'series'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    image = db.Column(db.String(60), nullable=False, default = 'defaultseries.jpg')
    blindboxes = db.relationship('Blindbox', backref='Series', cascade="all, delete-orphan")

    def __repr__(self):
        return f"ID: {self.id}\nName: {self.name}"


class Blindbox(db.Model):
    __tablename__ = 'blindboxes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64),nullable=False)
    description = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(60), nullable=False)
    price = db.Column(db.Float, nullable=False)
    release_date = db.Column(db.DateTime, nullable=False)
    brand=db.Column(db.String(60), nullable=False)
    size=db.Column(db.String(60), nullable=False)
    material=db.Column(db.String(60), nullable=False)
    set_quantity=db.Column(db.Integer, nullable=False)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'))
    
    def __repr__(self):
        return f"ID: {self.id}\nName: {self.name}\nDescription: {self.description}\nPrice: ${self.price}\nSeries: {self.series_id}\nRelease Date: {self.release_date}"

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean, default=False)
    firstname = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    address = db.Column(db.String(128))
    phone = db.Column(db.String(32))
    total_cost = db.Column(db.Float)
    date = db.Column(db.DateTime)
    email = db.Column(db.String(128))
    # blindboxes = db.relationship("Blindbox", backref="orders")
    order_details = db.relationship("OrderDetail", backref="orders")
    
    def __repr__(self):
        return f"ID: {self.id}\nStatus: {self.status}\nFirst Name: {self.firstname}\nSurname: {self.surname}\nAddress: {self.address}\nPhone: {self.phone}\nDate: {self.date}\nBlindboxes: {self.blindboxes}\nTotal Cost: ${self.total_cost}"
    
class OrderDetail(db.Model):
    __tablename__ = 'orderdetails'
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), primary_key=True)
    blindbox_id = db.Column(db.Integer, db.ForeignKey('blindboxes.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    # order = db.relationship("Order", backref=db.backref("order_details", cascade="all, delete-orphan"))
    blindbox = db.relationship("Blindbox", backref="order_details")
