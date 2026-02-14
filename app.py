from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# إعداد التطبيق
app = Flask(__name__)
CORS(app)

# إعداد قاعدة البيانات
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")
gine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# نموذج المنتج
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    image_url = Column(String(500))
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

# API: الحصول على جميع المنتجات
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        db = SessionLocal()
        products = db.query(Product).all()
        db.close()
        
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'image_url': p.image_url,
            'category': p.category
        } for p in products]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: إضافة منتج جديد
@app.route('/api/products', methods=['POST'])
def add_product():
    try:
        data = request.json
        db = SessionLocal()
        
        new_product = Product(
            name=data.get('name'),
            description=data.get('description'),
            price=float(data.get('price', 0)),
            image_url=data.get('image_url'),
            category=data.get('category')
        )
        
        db.add(new_product)
        db.commit()
        product_id = new_product.id
        db.close()
        
        return jsonify({'message': 'تم إضافة المنتج بنجاح', 'id': product_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: حذف منتج
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        db = SessionLocal()
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return jsonify({'error': 'المنتج غير موجود'}), 404
        
        db.delete(product)
        db.commit()
        db.close()
        
        return jsonify({'message': 'تم حذف المنتج بنجاح'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: تحديث منتج
@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.json
        db = SessionLocal()
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return jsonify({'error': 'المنتج غير موجود'}), 404
        
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = float(data.get('price', product.price))
        product.image_url = data.get('image_url', product.image_url)
        product.category = data.get('category', product.category)
        
        db.commit()
        db.close()
        
        return jsonify({'message': 'تم تحديث المنتج بنجاح'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)