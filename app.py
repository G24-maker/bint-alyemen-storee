from flask import Flask, request, jsonify
from flask_cors import CORS
from peewee import *
from datetime import datetime
import os
from dotenv import load_dotenv

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

# إعداد قاعدة البيانات
if DATABASE_URL.startswith("sqlite"):
    db = SqliteDatabase(DATABASE_URL.replace("sqlite:///", ""))
else:
    db = SqliteDatabase("database.db")

# تعريف النموذج
class Product(Model):
    name = CharField(max_length=200)
    description = TextField(default="")
    price = FloatField()
    image_url = CharField(max_length=500, default="")
    category = CharField(max_length=100, default="عام")
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        database = db

# إنشاء الجداول
db.connect()
db.create_tables([Product], safe=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        db.execute_sql("SELECT 1")
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

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        products = Product.select().order_by(Product.created_at.desc())
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

@app.route('/api/products', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'price' not in data:
            return jsonify({'error': 'الاسم والسعر مطلوبان'}), 400
        
        product = Product.create(
            name=data.get('name'),
            description=data.get('description', ''),
            price=float(data.get('price')),
            image_url=data.get('image_url', ''),
            category=data.get('category', 'عام')
        )
        
        return jsonify({
            'message': 'تم إضافة المنتج بنجاح',
            'id': product.id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ تم إصلاح المسار هنا - إضافة <int:product_id>
@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        product = Product.get_or_none(Product.id == product_id)
        if not product:
            return jsonify({'error': 'المنتج غير موجود'}), 404
        
        data = request.get_json()
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = float(data.get('price', product.price))
        product.image_url = data.get('image_url', product.image_url)
        product.category = data.get('category', product.category)
        product.save()
        
        return jsonify({'message': 'تم تحديث المنتج بنجاح'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ تم إصلاح المسار هنا - إضافة <int:product_id>
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = Product.get_or_none(Product.id == product_id)
        if not product:
            return jsonify({'error': 'المنتج غير موجود'}), 404
        
        product.delete_instance()
        return jsonify({'message': 'تم حذف المنتج بنجاح'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
