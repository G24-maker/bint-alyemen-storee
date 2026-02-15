from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

# Create engine with proper configuration for SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Product Model
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    image_url = Column(String(500))
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Test database connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return jsonify({
            "status": "ok",
            "message": "السيرفر يعمل بكامل طاقته",
            "database": "متصل"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Get all products
@app.route('/api/products', methods=['GET'])
def get_products():
    db = SessionLocal()
    try:
        products = db.query(Product).order_by(Product.created_at.desc()).all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'image_url': p.image_url,
            'category': p.category,
            'created_at': p.created_at.isoformat() if p.created_at else None
        } for p in products]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# Add new product
@app.route('/api/products', methods=['POST'])
def add_product():
    db = SessionLocal()
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'price' not in data:
            return jsonify({'error': 'الاسم والسعر مطلوبان'}), 400
        
        new_product = Product(
            name=data.get('name'),
            description=data.get('description', ''),
            price=float(data.get('price')),
            image_url=data.get('image_url', ''),
            category=data.get('category', 'عام')
        )
        
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        return jsonify({
            'message': 'تم إضافة المنتج بنجاح',
            'id': new_product.id
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# Update product
@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({'error': 'المنتج غير موجود'}), 404
        
        data = request.get_json()
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = float(data.get('price', product.price))
        product.image_url = data.get('image_url', product.image_url)
        product.category = data.get('category', product.category)
        
        db.commit()
        return jsonify({'message': 'تم تحديث المنتج بنجاح'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# Delete product
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({'error': 'المنتج غير موجود'}), 404
        
        db.delete(product)
        db.commit()
        return jsonify({'message': 'تم حذف المنتج بنجاح'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
