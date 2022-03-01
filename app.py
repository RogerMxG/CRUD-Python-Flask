from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL
from flask import send_from_directory
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "Develoteca"
mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'crudpython'
app.config['MYSQL_DATABASE_PORT'] = 3306

mysql.init_app(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA

#Mostramos los elementos en el directorio
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

@app.route('/')
def index():
    sql = "SELECT * FROM `empleados`;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)

    #Realiza la muestra de todos los empleados de la DB en terminal
    empleados = cursor.fetchall()
    print(empleados)

    conn.commit()

    #Envío de datos de DB a index.html
    return render_template('empleados/index.html', empleados = empleados)

#Borrar id de la DB desde index.html
@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    # Buscamos la foto de acuerdo al id de la DB
    cursor.execute("SELECT foto FROM empleados WHERE id = %s", id)
    fila = cursor.fetchall()
    # Removemos la foto para actualizarla al id correspondiente
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))

    cursor.execute("DELETE FROM empleados WHERE id = %s", (id))
    conn.commit()
    return redirect('/') #Redireccionamos a la página principal

#Editar la información de un id de la DB desde index.html
@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id = %s", (id))

    # Realiza la muestra de todos los empleados de la DB
    empleados = cursor.fetchall()
    conn.commit()
    print(empleados)


    return render_template('empleados/edit.html', empleados = empleados)

#Actualizamos los datos de acuerdo al id de la DB en edit.html
@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    id = request.form['txtID']

    sql = "UPDATE empleados SET nombre = %s, correo = %s WHERE id = %s;"

    datos = (_nombre, _correo, id)

    conn = mysql.connect()
    cursor = conn.cursor()

    #Actualizar foto del empleado
    # Determinar si la foto existe y en que tiempo se agregó
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    # Verificamos que la foto no sea vacía y la guardamos en la carpeta uploads
    if _foto.filename != '':
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)

        #Buscamos la foto de acuerdo al id de la DB
        cursor.execute("SELECT foto FROM empleados WHERE id = %s", id)
        fila = cursor.fetchall()

        #Removemos la foto para actualizarla al id correspondiente
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        cursor.execute("UPDATE empleados SET foto = %s WHERE id = %s", (nuevoNombreFoto, id))
        conn.commit()

    cursor.execute(sql, datos)
    conn.commit()

    return redirect('/')

#Creamos un nuevo empleado en la DB en el archivo create.html
@app.route('/create')
def create():
    return render_template('empleados/create.html')

@app.route('/aboutme')
def aboutme():
    return render_template('empleados/aboutme.html')

#Creacmos la función POST para hacer inserciones a la tabla empleados en nuestra DB
@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    if _nombre == '' or _correo == '' or _foto == '':
        flash('Llena los datos de los campos para continuar')
        return redirect(url_for('create'))

    #Determinar si la foto existe y en que tiempo se agregó
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    #Verificamos que la foto no sea vacía y la guardamos en la carpeta uploads
    #Además, se asegura que la foto no se sobreescriba
    if _foto.filename != '':
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)


    sql = "INSERT INTO `empleados` (`nombre`, `correo`, `foto`) VALUES(%s, %s, %s);"

    datos = (_nombre,_correo,nuevoNombreFoto)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
