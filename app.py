import os
import logging
from flask import Flask
from config import Config
from extensions import db  # import db from extensions
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# ---------------------------
# Initialize Flask app
# ---------------------------
app = Flask(__name__)
app.config.from_object(Config)

# ---------------------------
# Ensure database exists
# ---------------------------
db_uri = app.config['SQLALCHEMY_DATABASE_URI']
# Extract database name from URI
db_name = db_uri.rsplit('/', 1)[-1]
engine_uri_without_db = db_uri.rsplit('/', 1)[0]

try:
    engine = create_engine(db_uri)
    conn = engine.connect()
    conn.close()
except OperationalError:
    # Database doesn't exist, create it
    engine = create_engine(engine_uri_without_db)
    conn = engine.connect()
    conn.execute(f"CREATE DATABASE {db_name}")
    conn.close()
    print(f"Database '{db_name}' created successfully.")

# ---------------------------
# Initialize database
# ---------------------------
db.init_app(app)  # initialize db with app

# ---------------------------
# Configure logging
# ---------------------------
os.makedirs(app.config['LOG_FOLDER'], exist_ok=True)
logging.basicConfig(
    filename=f"{app.config['LOG_FOLDER']}/app.log",
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# ---------------------------
# Register blueprints
# ---------------------------
# Import blueprints AFTER app and db are initialized
from controllers.file_controller import file_bp
app.register_blueprint(file_bp)

# ---------------------------
# Create database tables if they don't exist
# ---------------------------
with app.app_context():
    db.create_all()

# ---------------------------
# Run the app
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
