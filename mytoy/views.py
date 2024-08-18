from flask import Blueprint, render_template, url_for, request, session, flash, redirect
from .models import Series, Blindbox, Order, OrderDetail
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .forms import CheckoutForm
from . import db
from sqlalchemy import func

main_bp = Blueprint('main', __name__)

@main_bp.context_processor
def render_series():
    series=Series.query.order_by(Series.name).all()
    return dict(series=series)


@main_bp.route('/')
def index():
    last_month=(datetime.now()- relativedelta(months=1)).strftime("%Y.%m")
    current_month=datetime.now().strftime("%Y.%m")
    month=f"{last_month}-{current_month}"

    blindboxes = db.session.scalars(db.select(Blindbox).where(
        func.strftime('%Y.%m', Blindbox.release_date) == current_month or
        func.strftime('%Y.%m', Blindbox.release_date) == last_month
    ).order_by(Blindbox.name)).all()
    return render_template('index.html',blindboxes=blindboxes, month=month)

@main_bp.route('/order', methods=['POST', 'GET'])
def order():
    blindbox_id = request.values.get('blindbox_id')
    
    print(f'ID: {blindbox_id}')
    # retrieve order if there is one
    if 'order_id' in session.keys():
        order = db.session.scalar(db.select(Order).where(Order.id==session['order_id']))
        # order will be None if order_id/session is stale
    else:
        # there is no order
        order = None
    # create new order if needed
    if order is None:
        order = Order(status=False, firstname='', surname='', address='', phone='', total_cost=0, date=datetime.now())
        try:
            db.session.add(order)
            db.session.commit()
            session['order_id'] = order.id
        except:
            print('Failed trying to create a new order!')
            order = None
    
    # calculate total price
    total_price = 0
    if order is not None:
        for item in order.order_details:
            price=db.session.scalar(db.select(Blindbox.price).where(Blindbox.id==item.blindbox_id))
            total_price += item.quantity*price
        items= db.session.query(
        Blindbox.id,
        Blindbox.name, 
        Blindbox.image, 
        Blindbox.price,
        OrderDetail.quantity
        ).join(OrderDetail, OrderDetail.blindbox_id == Blindbox.id
        ).filter(OrderDetail.order_id == order.id).all()
    # are we adding an item?
    if blindbox_id is not None and order is not None:
        quant=int(request.values.get('quantity'))
        print(f'Values: {quant}')
        blindbox_id=int(blindbox_id)
        blindbox_ids = db.session.scalars(db.select(OrderDetail.blindbox_id).where(OrderDetail.order_id==order.id)) 
        
        #blindbox is a new item in basket     
        if blindbox_id not in blindbox_ids:            
            try:
                # order.blindboxes.append(blindbox)
                order_detail=OrderDetail(order_id=order.id, blindbox_id=blindbox_id, quantity=quant)
                db.session.add(order_detail)
                db.session.commit()
                flash('Item has been added to your basket.')
            except:
                flash('There was an issue adding the item to your basket',category='danger')
            return redirect(url_for('main.order'))
        else:
            try:
                q=OrderDetail.query.get((order.id, blindbox_id))
                q.quantity=q.quantity+quant
                db.session.commit()
                flash(f"Item's quantity updated.")
            except:
                flash('There was an issue adding the item to your basket',category='danger')
            return redirect(url_for('main.order'))
    return render_template('order.html', items=items, total_price=total_price)

@main_bp.route('/plus', methods=['POST'])
def plus():
    blindbox_id = int(request.values.get('blindbox_id'))
    order_id=session['order_id']
    q=OrderDetail.query.get((order_id, blindbox_id))
    q.quantity=q.quantity+1
    db.session.commit()
    flash(f"Item's quantity updated.")

    return redirect(url_for('main.order'))

@main_bp.route('/reduce', methods=['POST'])
def reduce():

    blindbox_id = int(request.values.get('blindbox_id'))
    order_id=session['order_id']
    q=OrderDetail.query.get((order_id, blindbox_id))
    if q.quantity<=1:
        return redirect(url_for('main.deleteitem', blindbox_id=blindbox_id))
    else:
        q.quantity=q.quantity-1
    db.session.commit()
    flash(f"Item's quantity updated.")
    return redirect(url_for('main.order'))

@main_bp.route('/deleteitem', methods=['POST', 'GET'])
def deleteitem():

    blindbox_id = int(request.values.get('blindbox_id'))
    order_id=session['order_id']
    order_detail=OrderDetail.query.get((order_id, blindbox_id))
    db.session.delete(order_detail)
    db.session.commit()
    flash('Item has been deleted.')

    return redirect(url_for('main.order'))

@main_bp.route('/checkout', methods=['POST','GET'])
def checkout():
    form = CheckoutForm() 
    if 'order_id' in session:
        order = db.get_or_404(Order, session['order_id'])
        if form.validate_on_submit():
            order.status = True
            order.firstname = form.firstname.data
            order.surname = form.surname.data
            order.phone = form.phone.data
            order.address = form.address.data
            total_cost = 0
            for item in order.order_details:
                price=db.session.scalar(db.select(Blindbox.price).where(Blindbox.id==item.blindbox_id))
                total_cost += item.quantity*price
                order.total_cost=total_cost
            order.date = datetime.now()
            order.email=form.email.data
            try:
                db.session.commit()
                del session['order_id']
                flash('Thank you! Your order has been forwarded to My Toy.')
                return redirect(url_for('main.index'))
            except:
                return 'There was an issue completing your order'
    return render_template('checkout.html', form=form)


@main_bp.route('/series/<int:series_id>', methods=['POST','GET'])
def series(series_id):

        blindboxes = db.session.scalars(db.select(Blindbox).where(Blindbox.series_id==series_id).order_by(Blindbox.name)).all()
        series_name=Series.query.filter_by(id=series_id).value(Series.name)
        return render_template('search.html', blindboxes=blindboxes, key=series_name)
    
    
@main_bp.route('/blindbox/<int:blindbox_id>', methods=['POST','GET'])
def blindbox(blindbox_id):
    
        blindbox = db.session.scalar(db.select(Blindbox).where(Blindbox.id==blindbox_id))
        series_name=Series.query.filter_by(id=blindbox.series_id).value(Series.name)
        return render_template('blindbox.html', blindbox=blindbox, series_name=series_name)    

@main_bp.route('/search', methods=['POST'])
def search():
        key_word=request.values.get('key_word')
        blindboxes = db.session.scalars(db.select(Blindbox).where(func.lower(Blindbox.name).contains(key_word.lower()))).all()
        if not blindboxes:
            return render_template('search.html', blindboxes=None, key=f"Search: '{key_word}'")
        else:
            return render_template('search.html', blindboxes=blindboxes, key=f"Search: '{key_word}'")