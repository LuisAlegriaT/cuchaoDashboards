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

###############################################################################Cliente y Auxiliares###############################################################
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

@app.route('/crearPersonal',methods =['POST'])
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

@app.route('/editarPersonal/<string:id>')
def editarPersonal(id):
    cursor= mysql.connection.cursor()
    cursor.execute('SELECT * FROM users JOIN departamento ON (users.departamento_id = departamento.id_departamento) where id={0}'.format(id))
    consulta= cursor.fetchall()
    cursor1=mysql.connection.cursor()
    cursor1.execute('SELECT * FROM departamento')
    consulta1 = cursor1.fetchall()
    return render_template('actualizarPersonal.html', personal= consulta[0], usuario =consulta1 )

@app.route('/actualizarPersonal/<string:id>',methods =['POST'])
def actualizarPersonal(id):
    if request.method=='POST':
        vnombre= request.form['txtnombre']
        vmail= request.form['txtmail']
        vdomicilio= request.form['txtdomicilio']
        vdepartamento= request.form['txtdepartamento']
        vtelefono= request.form['txttelefono']
        vtipo= request.form['txttipo']

        cursor=mysql.connection.cursor()
        cursor.execute('update users set nombre=%s ,mail=%s ,tipo=%s, domicilio=%s, departamento_id=%s ,telefono=%s where id=%s',(vnombre,vmail,vtipo, vdomicilio, vdepartamento,vtelefono,id))
        mysql.connection.commit()

    flash('Album se actualizo en la BD')
    return redirect(url_for('adminClandAux'))


@app.route('/eliminarPersonal/<string:id>')
def eliminarPersonal(id):
    cursor= mysql.connection.cursor()
    cursor.execute('delete from users where id = %s', [id])
    mysql.connection.commit()
    flash('Personal Eliminado de la base de datos')
    return redirect(url_for('adminClandAux'))


################################################################Departamentos###########################################################################################
            #CONSULTAR
@app.route('/adminDepartamentos')
def AdminDepa():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM departamento')
    consulta = cursor.fetchall()
    return render_template('adminDepartamentos.html', departamento=consulta)


            #INSERTAR
@app.route('/CrearDepartamentos')
def CrearDepa():
    return render_template('CrearDep.html')

@app.route('/insertDepas', methods=['POST'])
def insertarD():
    if request.method == ('POST'):
        depaName = request.form['nombreDepa']
        print(depaName)
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO departamento(nombre_departamento)values(%s)',[depaName])
        mysql.connection.commit()
        flash('Departamento Agregado')
        return redirect(url_for('AdminDepa'))


            #ACTUALIZAR

@app.route('/ActualizarDepartamentos/<id_departamento>')
def ActualizarDepa(id_departamento):
    cur= mysql.connection.cursor()
    cur.execute('SELECT * FROM departamento WHERE id_departamento = %s',[id_departamento])
    data=cur.fetchall()
    print(data)
    return render_template('ActualizarDep.html',departamento=data[0])

@app.route('/updateDepartamento/<id_departamento>', methods=['POST'])
def updateDepartamento(id_departamento, methods=['POST']):
    if request.method == 'POST':
        depaName= request.form['nombreDepa']
        cur=mysql.connection.cursor()
        cur.execute("""
            UPDATE departamento SET 
                nombre_departamento=%s
            WHERE id_departamento=%s
        """,(depaName,id_departamento))
        flash('Departamento Actualizado!')
        return redirect(url_for('AdminDepa'))

        #ELIMINAR 


@app.route('/EliminarDepartamentos/<string:id_departamento>')
def EliminarDepa(id_departamento):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM departamento WHERE id_departamento =  {0}'.format(id_departamento))
    mysql.connection.commit()
    flash('Departamento Eliminado')
    return redirect(url_for('AdminDepa'))

################################################################Tickets########################################################
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
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM users JOIN departamento ON (users.departamento_id = departamento.id_departamento) WHERE tipo = "AUXILIAR" ')
    consulta = cursor.fetchall()
    return render_template('adminAsignar.html', auxiliar=consulta)

#Arrancamos servidor
if __name__ == '__main__':
    app.run(port=3000,debug= True)


