from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flaskext.mysql import MySQL
from datetime import datetime
from pymysql.cursors import DictCursor
import os

app = Flask(__name__)
app.secret_key="ClaveSecreta"

# Configuracion DB
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] ='localhost'
app.config['MYSQL_DATABASE_USER'] ='root'
app.config['MYSQL_DATABASE_PASSWORD'] =''
app.config['MYSQL_DATABASE_BD'] ='sistema'

mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor(cursor = DictCursor) # Modificamos el cursor para tomar los datos como diccionario

CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA

@app.route('/uploads/<foto_empleado>')
def uploads(foto_empleado):
    return send_from_directory(app.config['CARPETA'], foto_empleado) # El metodo uploads nos dirige a la carpeta (CARPETA) y nos muestra la foto guardada en la variable nombre Foto

@app.route('/')
def index():
    sql = "SELECT * FROM `sistema`.`empleados`;" # Consulta a la base de datos de la tabla empleados

    cursor.execute(sql)
    
    db_empleados = cursor.fetchall() # Trae todos los datos
    print(db_empleados)
    conn.commit()
    
    return render_template('/empleados/index.html', empleados = db_empleados)

@app.route('/destroy/<int:id>')
def destroy(id):
    cursor.execute("DELETE FROM `sistema`.`empleados` WHERE id=%s", (id))
    conn.commit()
    return redirect('/')

@app.route('/create')
def create():
    
    return render_template('/empleados/create.html')

@app.route('/store', methods = ['POST'])
def storage():
    _nombre = request.form['nombre'] #Recibimos los datos del formulario
    _correo = request.form['correo']
    _foto = request.files['foto']
    
    if _nombre == '' or _correo =='' or _foto == '':
        flash('Debes completar los campos')
        return redirect(url_for('create'))
    
    now = datetime.now() # Obtenemos la fecha actual
    tiempo = now.strftime("%Y%H%M%S") # Fijamos la variable tiempo para marcar el a;o, hora, minutos y segundos actuales para nombrar la foto.
    
    if _foto.filename != '':
        nueva_foto = tiempo+_foto.filename
        _foto.save("uploads/"+nueva_foto)
      
    sql = "INSERT INTO `sistema`.`empleados` (`id`,`nombre`,`correo`, `foto`) VALUES (NULL, %s, %s, %s);" #Los valores %s son los que toma de lo que ingresa el usuario
    
    datos = (_nombre,_correo,nueva_foto) # Definimos las ubicaciones de cada uno de los campos. Con filename para tomar el nombre de la foto.

    cursor.execute(sql,datos)
    conn.commit()
    
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    sql = "SELECT * FROM `sistema`.`empleados` WHERE id = %s" # Consulta a la base de datos de la tabla empleados

    cursor.execute(sql,id)
    
    ed_empleado = cursor.fetchall() # Trae todos los datos
    conn.commit()
    return render_template('/empleados/edit.html', empleados = ed_empleado)

@app.route('/update', methods = ['POST'])
def update():

    _nombre = request.form['nombre'] 
    _correo = request.form['correo']
    _foto = request.files['foto']
    id=request.form['id']
        
    sql = "UPDATE `sistema`.`empleados` SET `nombre`=%s,`correo`=%s WHERE id=%s;"
    
    datos = (_nombre,_correo,id)

    conn = mysql.connect()
    cursor = conn.cursor()
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")
    
    if _foto.filename != '':
        nueva_foto = tiempo+_foto.filename
        _foto.save("uploads/"+nueva_foto)
    
        cursor.execute("SELECT foto FROM `sistema`.`empleados` WHERE id = %s",id) # Recuperamos la foto y actulizamos ese campo.
        fila =cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) # Con el metodo remove, eliminamos en la ubicacion donde se encuentra la foto almacenada, dicho archivo.
        
        cursor.execute("UPDATE `sistema`.`empleados` SET foto=%s WHERE id=%s",(nueva_foto,id)) # Seteamos el nuevo archivo de foto en la base de datos.
        conn.commit()
        
    cursor.execute(sql,datos)
    conn.commit()
    
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)