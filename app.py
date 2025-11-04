from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'glamour_life_secret_key_2024')

mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/glamour_life')
app.config["MONGO_URI"] = mongo_uri

app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['ALLOWED_EXTENSIONS'] = { 'jpg', 'webp'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

mongo = PyMongo(app)
departamentos = [
    {
        "id": "maquillaje", 
        "nombre": "Maquillaje", 
        "icono": "💄", 
        "color": "#e53e3e",
        "descripcion": "Productos de maquillaje de alta calidad"
    },
    {
        "id": "cabello", 
        "nombre": "Cuidado del Cabello", 
        "icono": "💇‍♀️", 
        "color": "#d69e2e",
        "descripcion": "Tratamientos y productos para tu cabello"
    },
    {
        "id": "piel", 
        "nombre": "Cuidado de la Piel", 
        "icono": "✨", 
        "color": "#38a169",
        "descripcion": "Productos para el cuidado facial y corporal"
    }
]

productos_db = {
    "maquillaje": [
        {
            "id": "labial_mate",
            "nombre": "Labial Matte Luxe",
            "precio": 450.00,
            "marca": "Glamour Cosmetics",
            "imagen": "labial.webp",
            "descripcion": "Labial de larga duración con acabado mate, disponible en 12 tonos vibrantes",
            "especificaciones": ["Larga duración", "Acabado mate", "12 tonos", "Hidratante"],
            "categoria": "Labiales"
        },
        {
            "id": "paleta_sombras",
            "nombre": "Paleta de Sombras Pro",
            "precio": 890.00,
            "marca": "Beauty Pro",
            "imagen": "sombras.jpg",
            "descripcion": "Paleta profesional con 16 sombras mates y brillantes para crear looks únicos",
            "especificaciones": ["16 sombras", "Mate y brillo", "Pigmentación alta", "Vegano"],
            "categoria": "Ojos"
        },
        {
            "id": "base_liquida",
            "nombre": "Base Líquida Full Coverage",
            "precio": 650.00,
            "marca": "Skin Perfect",
            "imagen": "base.webp",
            "descripcion": "Base de cobertura completa con fórmula ligera y finish natural",
            "especificaciones": ["Cobertura completa", "SPF 30", "24h duración", "No comedogénica"],
            "categoria": "Rostro"
        },
        {
            "id": "rimel_volumen",
            "nombre": "Rímel Volumen Extreme",
            "precio": 320.00,
            "marca": "Lash Queen",
            "imagen": "rimel.webp",
            "descripcion": "Rímel que proporciona volumen extremo sin grumos, efecto pestañas postizas",
            "especificaciones": ["Volumen extremo", "Sin grumos", "A prueba de agua", "Larga duración"],
            "categoria": "Ojos"
        }
    ],
    "cabello": [
        {
            "id": "shampoo_hidratante",
            "nombre": "Shampoo Hidratante Profundo",
            "precio": 380.00,
            "marca": "Hair Therapy",
            "imagen": "shampoo.webp",
            "descripcion": "Shampoo con keratina y aceite de argán para cabello seco y dañado",
            "especificaciones": ["Con keratina", "Aceite de argán", "Sin sulfatos", "Para cabello seco"],
            "categoria": "Limpieza"
        },
        {
            "id": "acondicionador_reparador",
            "nombre": "Acondicionador Reparador",
            "precio": 420.00,
            "marca": "Hair Therapy",
            "imagen": "acondicionador.webp",
            "descripcion": "Acondicionador reconstructor con proteínas y vitaminas para cabello débil",
            "especificaciones": ["Reconstructor", "Con proteínas", "Sin sal", "Desenredante"],
            "categoria": "Hidratación"
        },
        {
            "id": "tratamiento_keratina",
            "nombre": "Tratamiento de Keratina",
            "precio": 1200.00,
            "marca": "Professional Care",
            "imagen": "keratina.webp",
            "descripcion": "Tratamiento intensivo de keratina que alisa y repara el cabello por 3 meses",
            "especificaciones": ["Duración 3 meses", "Alisado natural", "Reparación profunda", "Brillo intenso"],
            "categoria": "Tratamientos"
        },
        {
            "id": "aceite_argan",
            "nombre": "Aceite de Argán Puro",
            "precio": 550.00,
            "marca": "Natural Beauty",
            "imagen": "aceite.webp",
            "descripcion": "Aceite 100% puro de argán para puntas abiertas y cabello quebradizo",
            "especificaciones": ["100% puro", "Multiusos", "Puntas abiertas", "Sin siliconas"],
            "categoria": "Aceites"
        }
    ],
    "piel": [
        {
            "id": "crema_hidratante",
            "nombre": "Crema Hidratante 24h",
            "precio": 680.00,
            "marca": "Skin Therapy",
            "imagen": "crema.webp",
            "descripcion": "Crema facial de hidratación intensiva con ácido hialurónico para todo tipo de piel",
            "especificaciones": ["24h hidratación", "Ácido hialurónico", "Todo tipo de piel", "No grasa"],
            "categoria": "Hidratación"
        },
        {
            "id": "serum_vitamina_c",
            "nombre": "Sérum de Vitamina C",
            "precio": 950.00,
            "marca": "Bright Skin",
            "imagen": "serum.webp",
            "descripcion": "Sérum antioxidante con 20% de vitamina C para unificar tono y reducir manchas",
            "especificaciones": ["20% Vitamina C", "Antioxidante", "Unifica tono", "Antienvejecimiento"],
            "categoria": "Sérums"
        },
        {
            "id": "protector_solar",
            "nombre": "Protector Solar FPS 50",
            "precio": 520.00,
            "marca": "Sun Care",
            "imagen": "protector.webp",
            "descripcion": "Protector solar facial de textura ligera con FPS 50 y protección UVA/UVB",
            "especificaciones": ["FPS 50", "Textura ligera", "Protección UVA/UVB", "No comedogénico"],
            "categoria": "Protección Solar"
        },
        {
            "id": "limpiador_facial",
            "nombre": "Limpiador Facial Suave",
            "precio": 350.00,
            "marca": "Pure Skin",
            "imagen": "gel.webp",
            "descripcion": "Gel limpiador suave que remueve impurezas sin resecar la piel",
            "especificaciones": ["PH balanceado", "Sin alcohol", "Piel sensible", "Dermatológicamente testeado"],
            "categoria": "Limpieza"
        }
    ]
}

def get_image_path(depto_id, imagen_nombre):
    """Obtiene la ruta completa de la imagen"""
    return f"img/productos/{depto_id}/{imagen_nombre}"

@app.route('/')
def index():
    if 'usuario' in session:
        return redirect(url_for('bienvenida'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email == "cliente@glamourlife.com" and password == "123456":
            session['usuario'] = {
                'id': '1',
                'nombre': 'Cliente Glamour Life',
                'email': email
            }
            session['carrito'] = []
            return redirect(url_for('bienvenida'))
        else:
            return render_template('login.html', error="Credenciales incorrectas")
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        session['usuario'] = {
            'id': '2',
            'nombre': f"{request.form['nombres']} {request.form['apellidos']}",
            'email': request.form['email']
        }
        session['carrito'] = []
        return redirect(url_for('bienvenida'))
    
    return render_template('registro.html')

@app.route('/bienvenida')
def bienvenida():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('bienvenida.html', usuario=session['usuario'])

@app.route('/departamentos')
def departamentos_view():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('departamentos.html', departamentos=departamentos)

@app.route('/productos/<depto_id>')
def productos(depto_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    depto = next((d for d in departamentos if d['id'] == depto_id), None)
    if not depto:
        return "Departamento no encontrado", 404
    
    productos_depto = productos_db.get(depto_id, [])
    
    for producto in productos_depto:
        producto['imagen_path'] = get_image_path(depto_id, producto['imagen'])
    
    return render_template('productos.html', 
                         productos=productos_depto, 
                         departamento=depto)

@app.route('/producto/<depto_id>/<producto_id>')
def producto_detalle(depto_id, producto_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    productos_depto = productos_db.get(depto_id, [])
    producto = next((p for p in productos_depto if p['id'] == producto_id), None)
    
    if not producto:
        return "Producto no encontrado", 404
    
    producto['imagen_path'] = get_image_path(depto_id, producto['imagen'])
    depto = next((d for d in departamentos if d['id'] == depto_id), None)
    
    return render_template('producto_detalle.html', 
                         producto=producto, 
                         departamento=depto)

@app.route('/agregar_carrito', methods=['POST'])
def agregar_carrito():
    if 'usuario' not in session:
        return jsonify({'success': False, 'message': 'Debe iniciar sesión'})
    
    depto_id = request.form['depto_id']
    producto_id = request.form['producto_id']
    cantidad = int(request.form.get('cantidad', 1))
    
    productos_depto = productos_db.get(depto_id, [])
    producto = next((p for p in productos_depto if p['id'] == producto_id), None)
    
    if not producto:
        return jsonify({'success': False, 'message': 'Producto no encontrado'})
    
    if 'carrito' not in session:
        session['carrito'] = []
    
    carrito_item = next((item for item in session['carrito'] 
                        if item['producto_id'] == producto_id and item['depto_id'] == depto_id), None)
    
    if carrito_item:
        carrito_item['cantidad'] += cantidad
    else:
        session['carrito'].append({
            'producto_id': producto_id,
            'depto_id': depto_id,
            'nombre': producto['nombre'],
            'precio': producto['precio'],
            'imagen': producto['imagen'],
            'imagen_path': get_image_path(depto_id, producto['imagen']),
            'cantidad': cantidad,
            'marca': producto.get('marca', ''),
            'categoria': producto.get('categoria', '')
        })
    
    session.modified = True
    
    return jsonify({
        'success': True, 
        'carrito_count': len(session['carrito']),
        'message': f'{producto["nombre"]} agregado al carrito'
    })

@app.route('/carrito')
def carrito():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    carrito = session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    
    return render_template('carrito.html', carrito=carrito, total=total)

@app.route('/actualizar_carrito', methods=['POST'])
def actualizar_carrito():
    if 'usuario' not in session:
        return jsonify({'success': False})
    
    producto_id = request.form['producto_id']
    depto_id = request.form['depto_id']
    nueva_cantidad = int(request.form['cantidad'])
    
    carrito = session.get('carrito', [])
    
    if nueva_cantidad <= 0:
        session['carrito'] = [item for item in carrito 
                             if not (item['producto_id'] == producto_id and item['depto_id'] == depto_id)]
    else:
        for item in carrito:
            if item['producto_id'] == producto_id and item['depto_id'] == depto_id:
                item['cantidad'] = nueva_cantidad
                break
    
    session.modified = True
    
    carrito_actualizado = session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito_actualizado)
    
    return jsonify({
        'success': True, 
        'total': total,
        'carrito_count': len(carrito_actualizado)
    })

@app.route('/eliminar_del_carrito/<depto_id>/<producto_id>')
def eliminar_del_carrito(depto_id, producto_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    session['carrito'] = [item for item in session['carrito'] 
                         if not (item['producto_id'] == producto_id and item['depto_id'] == depto_id)]
    session.modified = True
    
    return redirect(url_for('carrito'))

@app.route('/pago')
def pago():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    carrito = session.get('carrito', [])
    if not carrito:
        return redirect(url_for('carrito'))
    
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    return render_template('pago.html', carrito=carrito, total=total)

@app.route('/procesar_pago', methods=['POST'])
def procesar_pago():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    return redirect(url_for('procesando_pago'))

@app.route('/procesando_pago')
def procesando_pago():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('procesando_pago.html')

@app.route('/pago_exitoso')
def pago_exitoso():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    session['carrito'] = []
    session.modified = True
    
    return render_template('pago_exitoso.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)