from flask import Flask, render_template, request, redirect, url_for
from models import db, Store, Section, Item, seed_database
import os

app = Flask(__name__)
# Uses a local SQLite file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    seed_database()

@app.route('/')
def index():
    sections = Section.query.all()
    return render_template('index.html', sections=sections)

@app.route('/section/<int:section_id>', methods=['GET', 'POST'])
def manage_section(section_id):
    section = Section.query.get_or_404(section_id)
    
    if request.method == 'POST':
        for item in section.items:
            # Update quantity based on form input
            qty = request.form.get(f'item_{item.id}', 0, type=int)
            item.quantity_needed = qty
        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('section.html', section=section)

@app.route('/shopping_list')
def shopping_list():
    # Only pull items where quantity > 0
    items_needed = Item.query.filter(Item.quantity_needed > 0).all()
    
    # Group items strictly by store
    grouped_list = {}
    for item in items_needed:
        store_name = item.store.name
        if store_name not in grouped_list:
            grouped_list[store_name] = []
        grouped_list[store_name].append(item)
        
    return render_template('summary.html', grouped_list=grouped_list)

@app.route('/clear_list', methods=['POST'])
def clear_list():
    # Resets all inventory quantities to 0 after shopping is done
    items = Item.query.all()
    for item in items:
        item.quantity_needed = 0
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # host='0.0.0.0' allows external access from your mobile device on the local network
    app.run(host='0.0.0.0', port=5001, debug=True)