from app import app, db  # Adjust import according to your app structure

with app.app_context():
    db.create_all()
    print("Tables created successfully!")