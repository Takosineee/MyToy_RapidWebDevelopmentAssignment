from flask import Blueprint,render_template
from . import db
from .models import Series, Blindbox, Order, OrderDetail
import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dbseed')
def dbseed():
    b1 = Blindbox(series_id=1, image='s3.jpg', price=20.00,\
        release_date=datetime.datetime(2023, 5, 17),\
        name='Sanrio New Rhyme Flower Dress',\
        material='PVC/ABS',\
        brand='MINISO',\
        set_quantity=6,\
        size='4-9cm',\
        description= 'Sanrio character figures with rhyme flower dress theme.') 
    b2 = Blindbox(series_id=4, image='pm3.jpg', price=20.00,\
        release_date=datetime.datetime(2024, 5, 13),\
        name='Pokemon Welcome Back Collection',\
        material='PVC/ABS',\
        brand='Re-Ment',\
        set_quantity=6,\
        size='6-8cm',\
        description= 'Pokemon figures with Welcome Back theme.') 
    

    try:
        db.session.add(b1)
        db.session.add(b2)
        
        db.session.commit()
    except:
        return 'There was an issue adding a Blindbox in dbseed function'

    return 'DATA LOADED'

@admin_bp.route('/update')
def update():
    
    blindbox=Blindbox.query.get(8)
    blindbox.name='Pokemon Aqua Bottle Collection Part 2'
    
    try:
        db.session.commit()
    except:
        return 'There was an issue adding a Blindbox in dbseed function'

    return 'DATA LOADED'