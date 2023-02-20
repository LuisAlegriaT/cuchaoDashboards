#importar el framework 
from colorama import Cursor
from flask import Flask, render_template, request ,redirect,url_for,flash 
from flask_mysqldb import MySQL


#inicializar variable usar flask
app= Flask(__name__, template_folder='views')

#configuracion de la conexion 
app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']= ''
app.config['MYSQL_DB']= 'macuindb'
mysql= MySQL(app)
app.secret_key='mysecretkey'

#Cliente y Auxiliares
@app.route('/')
def adminClandAux():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM users JOIN departamento WHERE (users.departamento_id = departamento.id_departamento)')
    consulta = cursor.fetchall()
    return render_template('adminClandAux.html', usuario=consulta)

@app.route('/loginCrear')
def loginCrear():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM departamento')
    consulta = cursor.fetchall()
    return render_template('crearPersonal.html', usuario=consulta)

@app.route('/crearPersonal', methods =['POST'])
def crearPersonal():
    if request.method == 'POST':
        vnombre= request.form['txtnombre']
        vmail= request.form['txtmail']
        vdomicilio= request.form['txtdomicilio']
        vdepartamento= request.form['txtdepartamento']
        vtelefono= request.form['txttelefono']
        vtipo= request.form['txttipo']
        print(vnombre,vmail,vdomicilio,vdepartamento,vtelefono,vtipo)

        cursor=mysql.connection.cursor()
        cursor.execute('insert into users(nombre ,mail ,tipo, domicilio, departamento_id ,telefono)values (%s,%s,%s,%s,%s,%s)', 
        (vnombre,vmail,vtipo, vdomicilio, vdepartamento,vtelefono)) #%s son para las cadenas
        mysql.connection.commit()
    
    flash('Album almacenado en la BD')
    return redirect(url_for('adminClandAux')) 

@app.route('/actualizarPersonal')
def actualizarPersonal():
    return render_template('actualizarPersonal.html')


#Departamentos 
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

#Tickets
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

#Arrancamos servidor
if __name__ == '__main__':
    app.run(port=3000,debug= True)


