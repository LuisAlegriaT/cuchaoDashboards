#importar el framework 
from colorama import Cursor
from flask import Flask, render_template, request ,redirect,url_for,flash 
from flask_mysqldb import MySQL


#inicializar variable usar flask
app= Flask(__name__, template_folder='views', render_template='views' )

#configuracion de la conexion 
app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']= ''
app.config['MYSQL_DB']= 'macuindb'
mysql= MySQL(app)
app.secret_key='mysecretkey'

@app.route('/')
def adminClandAux():
    cursor=mysql.connection.cursor()
    cursor.execute('select *from users')
    consulta = cursor.fetchall()
    return render_template('adminClandAux.html', usuario=consulta)


@app.route('/adminDepartamentos')
def AdminDepa():
    return render_template('adminDepartamentos.html')

@app.route('/CrearDepartamentos')
def CrearDepa():
    return render_template('CrearDep.html')

@app.route('/ActualizarDepartamentos')
def ActualizarDepa():
    return render_template('ActualizarDep.html')

@app.route('/EliminarDepartamentos')
def EliminarDepa():
    return render_template('EliminarDep.html')

@app.route('/adminTickets')
def AdminTickets():
    return render_template('adminTickets.html')

@app.route('/adminComentario')
def AdminComentario():
    return render_template('adminComentario.html')

@app.route('/ComentarioCliente')
def ComentarioCliente():
    return render_template('ComentarioCliente.html')


@app.route('/ComentarioAuxiliar')
def ComentarioAuxiliar():
    return render_template('ComentarioAuxiliar.html')

@app.route('/adminAsignar')
def adminAsignar():
    return render_template('adminAsignar.html')

@app.route('/crearPersonal')
def crearPersonal():
    return render_template('crearPersonal.html')

@app.route('/actualizarPersonal')
def actualizarPersonal():
    return render_template('actualizarPersonal.html')



#Arrancamos servidor
if __name__ == '__main__':
    app.run(port=3000,debug= True)


