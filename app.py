from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId

# configuramos la app de flask y una clave secreta para que funcionen los mensajes flash
app = Flask(__name__)
app.secret_key = "super_secret_key_marvel_dc"

# nos conectamos a la base de datos de mongo que está corriendo en docker
client = MongoClient('mongodb://superheroe_db:27017/')
db = client['super_db']
collection = db['personajes']

# ruta principal: traemos absolutamente todos los personajes de la base y los mandamos al index
@app.route('/')
def index():
    personajes = list(collection.find())
    return render_template('index.html', personajes=personajes, casa="TODOS")

# filtro de marvel: buscamos en la base solo a los que tienen la etiqueta 'MARVEL'
@app.route('/marvel')
def marvel():
    personajes = list(collection.find({'casa': 'MARVEL'}))
    return render_template('index.html', personajes=personajes, casa="MARVEL")

# filtro de dc: lo mismo que arriba, pero buscamos solo a los de 'DC'
@app.route('/dc')
def dc():
    personajes = list(collection.find({'casa': 'DC'}))
    return render_template('index.html', personajes=personajes, casa="DC")

# vista de detalle: usamos el id (el dni del personaje) para buscar uno solo y mostrar su info completa
@app.route('/detalle/<id>')
def detalle(id):
    personaje = collection.find_one({'_id': ObjectId(id)})
    return render_template('detalle.html', p=personaje)

# abrir el formulario para uno nuevo: mandamos 'p=None' para que el formulario se vea vacío
@app.route('/add')
def add():
    return render_template('form.html', p=None)

# abrir el formulario para editar: buscamos al personaje por id y mandamos su data para rellenar los campos
@app.route('/edit/<id>')
def edit(id):
    personaje = collection.find_one({'_id': ObjectId(id)})
    return render_template('form.html', p=personaje)

# la parte que guarda: acá procesamos el formulario cuando el usuario le da al botón de guardar
@app.route('/save', methods=['POST'])
def save():
    try:
        # chequeamos si el formulario trae un id (si trae, es porque estamos editando uno viejo)
        pid = request.form.get('id')
        
        # armamos un paquete (diccionario) con toda la info que el usuario escribió en la web
        datos = {
            "nombre": request.form.get('nombre', 'Sin nombre'),
            "nombreReal": request.form.get('nombreReal', ''),
            "anioAparicion": request.form.get('anioAparicion', 0),
            "casa": request.form.get('casa', 'MARVEL'),
            "biografia": request.form.get('biografia', ''),
            "equipamiento": request.form.get('equipamiento', ''),
            "imagenes": request.form.get('imagenes', 'marvel.png').split(',')
        }
        
        if pid:
            # si el id existe, le decimos a mongo que actualice los datos de ese personaje
            collection.update_one({'_id': ObjectId(pid)}, {'$set': datos})
            flash("¡Actualizado!", "success")
        else:
            # si no hay id, es un personaje nuevo, así que lo insertamos de cero
            collection.insert_one(datos)
            flash("¡Guardado correctamente!", "success")
            
    except Exception as e:
        # si algo sale mal (ej: se corta la base), avisamos del error
        flash(f"Error: {e}", "danger")
    
    # después de guardar, volvemos siempre a la página principal
    return redirect(url_for('index'))

# borrar: le pasamos el id y le pedimos a mongo que lo saque de la colección
@app.route('/delete/<id>')
def delete(id):
    collection.delete_one({'_id': ObjectId(id)})
    flash("Personaje eliminado correctamente 🗑️", "success")
    return redirect(url_for('index'))

# prendemos el servidor en el puerto 5001 y activamos el modo debug para ver errores en tiempo real
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)