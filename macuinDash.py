#importar el framework 
from colorama import Cursor
from flask import Flask, render_template, request ,redirect,url_for,flash, session
from flask_mysqldb import MySQL
from flask_session import Session




#inicializar el Framework
app= Flask(__name__, template_folder='views')



#iniciar el Depurador Automaticamente

# Flask sessions
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


#configuracion de la conexion 
app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']= ''
app.config['MYSQL_DB']= 'macuindb'

mysql= MySQL(app)
app.secret_key='mysecretkey'


#------- Configuraciones Roles de Usuaio-----#

class user():
    def __init__(self,status,nombre,password)->None:
        self.status = status
        self.nombre = nombre
        self.password = password

class user1():
    def __init__(self,idmed, nombre, rol)->None:
        self.idmed = idmed
        self.nombre = nombre
        self.rol = rol




#/////////////////RUTAS////////////////#


#--------Ruta General--------#
@app.route('/')
def log():
    return render_template('login.html')


#--------Login--------#
@app.route('/login', methods=["POST"])
def login():
    if request.method == 'POST':
        usuario = request.form['txtuser']
        pas = request.form['txtpassword']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT tipoId, nombre, password FROM users where nombre = %s and password = %s',(usuario,pas))
        
        mysql.connection.commit()
        account = cursor.fetchone()
        
        if account:
            session['id'] = account[0] # tipo
            session['usuario'] = account[1] # usuario
            session['pas'] = account[2] # contraseña
            print(account[0],account[1],account[2])
            #-----------Administradores
            if(account[0] == 1 and account[1] == usuario and account[2] == pas):
                return render_template('adminClandAux.html') # vista Admin
              
            #-----------Auxiliares
            
            if(account[0] == 2 and account[1] == usuario and account[2] == pas):
                return render_template('index.html') # Vista Auxiliar
          
            #-----------Clientes
            if(account[0] == 3 and account[1] == usuario and account[2] == pas):
                return render_template('adminDepartamentos.html') # vista clientes
                              
        else:
            flash('Datos incorrectos')
            return render_template('login.html')
        
        
@app.route('/Admin/<string:id>')
def Admin(id):
    if session['id'] == None:
        return render_template('login.html')
    else:
        return render_template('adminTickets.html', user = user)  
 
@app.route('/logout')
def logout():
    session['id']=None
    return render_template('login.html') 



#Cliente y Auxiliares
@app.route('/adminClandAux')
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
        cursor.execute('insert into users(nombre ,mail ,status, domicilio, departamento_id ,telefono)values (%s,%s,%s,%s,%s,%s)', 
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
def updateDepartamento(id_departamento):
    if request.method == 'POST':
        depaName= request.form['nombreDepa']
        print(depaName)
        print(id_departamento)
        cur=mysql.connection.cursor()
        cur.execute("""
            UPDATE departamento SET 
                nombre_departamento = %s
            WHERE id_departamento = %s
        """,(depaName,id_departamento))
        mysql.connection.commit()
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
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT id_ticket, fecha, detalle,estatus, clasificacion, user_idCliente, nombre FROM ticket JOIN users ON (ticket.user_idCliente = users.id) ')
    consulta = cursor.fetchall()
    return render_template('adminTickets.html', ticket=consulta)

@app.route('/adminComentario/<id_ticket>')
def AdminComentario(id_ticket): 
    id_t=id_ticket   
    print(id_t)
    return render_template('adminComentario.html', ticket=id_t)


    #COMENTARIO PARA AUXILIAR
@app.route('/ComentarioAuxiliar/<ticket>',methods=['POST'])
def ComentarioAuxiliar(ticket):
    ticket=ticket
    cur= mysql.connection.cursor()
    cur.execute('SELECT nombre FROM users INNER JOIN ticketaux ON users.id = ticketaux.userAux_id INNER JOIN ticket ON ticketaux.ticket_idAux = ticket.id_ticket WHERE ticket.id_ticket = %s',[ticket])
    data=cur.fetchall()
    print(ticket)
    return render_template('ComentarioAuxiliar.html', ticket1=data,ticket=ticket)

@app.route('/inssertComentario/<ticket>',methods=['POST'])
def insertComentario(ticket):
  if request.method=='POST':
        #ticket_id=ticket  
        comentarioA= request.form['txtComentarioA'] 
        print(ticket)
        print(comentarioA)
        cursor=mysql.connection.cursor()
        cursor.execute('UPDATE ticket SET comentariosAux = %s WHERE id_ticket = %s',(comentarioA, ticket))
        mysql.connection.commit()
        return redirect(url_for('AdminTickets'))

        #COMENTARIO CLIENTE
@app.route('/ComentarioCliente/<ticket>',methods=['POST'])
def ComentarioCliente(ticket):
    ticket=ticket
    cur= mysql.connection.cursor()
    cur.execute('SELECT nombre from users INNER JOIN ticket ON ticket.user_idCliente = users.id where ticket.id_ticket=%s',[ticket])
    data=cur.fetchall()
    print(ticket)
    return render_template('ComentarioCliente.html', ticket1=data,ticket=ticket)

@app.route('/insertComentarioC/<ticket>',methods=['POST'])
def insertComentarioC(ticket):
  if request.method=='POST':
        #ticket_id=ticket  
        comentarioC= request.form['txtComentarioC'] 
        print(ticket)
        print(comentarioC)
        cursor=mysql.connection.cursor()
        cursor.execute('UPDATE ticket SET comentariosCliente = %s WHERE id_ticket = %s',(comentarioC, ticket))
        mysql.connection.commit()
        return redirect(url_for('AdminTickets'))


        #ASIGNAR AUXILIAR

@app.route('/adminAsignar/<id_ticket>')
def adminAsignar(id_ticket):
    ticketRecived=id_ticket
    cur=mysql.connection.cursor()
    cur.execute('SELECT users.nombre, (SELECT COUNT(ticketaux.userAux_id) FROM ticketaux WHERE users.id = ticketaux.userAux_id) AS tickets_Auxiliar FROM users WHERE users.tipo="AUXILIAR"')
    consultaAux=cur.fetchall()
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE tipo = "AUXILIAR" ')
    consulta = cursor.fetchall()
    return render_template('adminAsignar.html', auxiliar=consulta, ticketSend=ticketRecived,ticketsAux=consultaAux)

@app.route('/asignarTicket/<ticketSend>', methods=['POST'])
def asignarTicket(ticketSend):
    if request.method=='POST':
        print(ticketSend)
        auxiliar=request.form['txtAuxiliar']
        print(auxiliar)
        cursor=mysql.connection.cursor()
        cursor.execute('INSERT INTO ticketaux (ticket_idAux, userAux_id) VALUES (%s, %s)',(ticketSend, auxiliar))
        mysql.connection.commit()
        return redirect(url_for('AdminTickets'))
    
    #REPORTE
@app.route('/Reportes')
def Reportes():
    return render_template('adminReporte.html')


################################## PERFIL AUXILIAR #################################################
@app.route('/MiPerfil')
def miPerfil():
    return render_template('miPerfil.html')




################################## CLIENTE #############################################3
@app.route('/perfilCliente')
def perfilCliente():
    return render_template('perfilCliente.html')


@app.route('/adminSolicitud')
def adminSolicitud():
    return render_template('adminSolicitud.html')

@app.route('/crearSolicitud')
def crearSolicitud():
    return render_template('crearSolicitud.html')




#Arrancamos servidor
if __name__ == '__main__':
    app.run(port=3000,debug= True)


