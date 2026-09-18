from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    items = db.relationship('Item', backref='store', lazy=True)

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    pin = db.Column(db.String(4), nullable=True) # Optional 4-digit PIN
    items = db.relationship('Item', backref='section', lazy=True, cascade="all, delete-orphan")

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity_needed = db.Column(db.Integer, default=0)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)

def seed_database():
    if Store.query.first() is None:
        stores = ["Sam's", "Costco", "Restaurant Depot", "Vietnamese markets", "Walmart"]
        for s in stores:
            db.session.add(Store(name=s))

        sections = ["Drink makers", "Chu Sang", "Co Mai", "Co Hong", "Juan", "front servers", "owner order"]
        for s in sections:
            db.session.add(Section(name=s))

        db.session.commit()

        sam_store = Store.query.filter_by(name="Sam's").first()
        depot_store = Store.query.filter_by(name="Restaurant Depot").first()
        drinks_section = Section.query.filter_by(name="Drink makers").first()
        juan_section = Section.query.filter_by(name="Juan").first()

        db.session.add_all([
            Item(name="whip cream", store=sam_store, section=drinks_section),
            Item(name="16oz cups", store=depot_store, section=juan_section)
        ])
        db.session.commit()