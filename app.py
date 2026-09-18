from flask import Flask, render_template, request, redirect, url_for
from models import db, Store, Section, Item, seed_database
import os
import difflib # for searching bar

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

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        item_name = request.form.get('name')
        store_id = request.form.get('store_id', type=int)
        section_id = request.form.get('section_id', type=int)
        
        if item_name and store_id and section_id:
            new_item = Item(name=item_name, store_id=store_id, section_id=section_id, quantity_needed=0)
            db.session.add(new_item)
            db.session.commit()
        return redirect(url_for('admin_panel'))
        
    items = Item.query.all()
    stores = Store.query.all()
    sections = Section.query.all()
    return render_template('admin.html', items=items, stores=stores, sections=sections)

@app.route('/admin/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/search')
def search_items():
    query = request.args.get('q', '').strip()
    results = []
    
    if query:
        all_items = Item.query.all()
        # Create a dictionary mapping item names to the item objects
        item_dict = {item.name: item for item in all_items}
        
        # Find close matches for spelling mistakes (cutoff=0.3 means a loose match)
        close_names = difflib.get_close_matches(query, item_dict.keys(), n=8, cutoff=0.3)
        results = [item_dict[name] for name in close_names]
        
        # Fallback: if substring match isn't in close_names, add it if it contains the query letters
        for item in all_items:
            if query.lower() in item.name.lower() and item not in results:
                results.append(item)
                
    return render_template('search.html', query=query, results=results)

if __name__ == '__main__':
    # host='0.0.0.0' allows external access from your mobile device on the local network
    app.run(host='0.0.0.0', port=5001, debug=True)