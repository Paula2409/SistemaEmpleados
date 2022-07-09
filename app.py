# Importamos modulos para el proyecto
# Resquest lo importamos por que toda la informacion que se va a procesar a traves del HTML va a ser un ENVIO de informacion. Este envio se maneja como 'request'(solicitud de informacion).
# Redirect: nos permite redireccionar a la url desde donde vino

from flask import Flask, render_template, request, redirect, url_for
from flaskext.mysql import MySQL
from datetime import datetime
from pymysql.cursors import DictCursor

app = Flask(__name__)

# Configuracion DB
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] ='localhost'
app.config['MYSQL_DATABASE_USER'] ='root'
app.config['MYSQL_DATABASE_PASSWORD'] =''
app.config['MYSQL_DATABASE_BD'] ='sistema'

mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor(cursor = DictCursor) # Modificamos el cursor para tomar los datos como diccionario

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
    
    now = datetime.now() # Obtenemos la fecha actual
    tiempo = now.strftime("%Y%H%M%S") # Fijamos la variable tiempo para marcar el a;o, hora, minutos y segundos actuales para nombrar la foto.
    
    if _foto.filename != '':
        nueva_foto = tiempo+_foto.filename
        _foto.save("uploads/"+nueva_foto)
      
    sql = "INSERT INTO `sistema`.`empleados` (`id`,`nombre`,`correo`, `foto`) VALUES (NULL, %s, %s, %s);" #Los valores %s son los que toma de lo que ingresa el usuario
    
    datos = (_nombre,_correo,nueva_foto) # Definimos las ubicaciones de cada uno de los campos. Con filename para tomar el nombre de la foto.

    cursor.execute(sql,datos)
    conn.commit()
    
    return render_template('/empleados/index.html')



if __name__ == "__main__":
    app.run(debug=True)