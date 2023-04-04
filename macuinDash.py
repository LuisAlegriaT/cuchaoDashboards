#importar el framework 
from colorama import Cursor
from flask import Flask, render_template, request ,redirect,url_for,flash, session, make_response
from flask_mysqldb import MySQL
from flask_session import Session
from io import BytesIO





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




################################/////////////////RUTAS////////////////############################################


#--------Ruta General--------#
@app.route('/')
def log():
    return render_template('login.html')


#####################################--------Login--------##############################
@app.route('/login', methods=["POST"])
def login():
    if request.method == 'POST':
        usuario = request.form['txtuser']
        pas = request.form['txtpassword']
        cursor = mysql.connection.cursor()

        cursor.execute('SELECT tipoId, nombre, pass, id  FROM users where nombre = %s and pass = %s',(usuario,pas))
       
        mysql.connection.commit()
        account = cursor.fetchone()
        
        if account:

            session['rol'] = account[0] # tipo
            session['usuario'] = account[1] # usuario
            session['pas'] = account[2] 
            session['id'] = account[3]# contraseña
            userlog = account[3]
            #print(account[0],account[1],account[2])
            print(userlog)
            
            #-----------Administradores
            if(account[0] == 1 and account[1] == usuario and account[2] == pas):
                return redirect(url_for('adminClandAux',loguser=userlog)) # vista Admin
              
            #-----------Auxiliares
            
            if (account[0] == 2 and account[1] == usuario and account[2] == pas):
                return redirect(url_for('perfilAuxiliar',loguser=userlog)) # Vista Auxiliar
          
            #-----------Clientes
            if(account[0] == 3 and account[1] == usuario and account[2] == pas):
                return redirect(url_for('perfilCliente',loguser=userlog)) # vista clientes
                              
        else:
            flash('Datos incorrectos')
            return redirect(url_for('log'))
        
        
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
@app.route('/adminClandAux/<string:loguser>')
def adminClandAux(loguser):
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM departamento INNER JOIN users ON departamento.id_departamento = users.departamento_id INNER JOIN tipousers ON users.tipoId = tipousers.idTipo')
    consulta = cursor.fetchall()



    return render_template('adminClandAux.html', usuario=consulta, loguser=loguser)

@app.route('/loginCrear/<string:loguser>')
def loginCrear(loguser):
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM departamento')
    consulta = cursor.fetchall()
    cursor2=mysql.connection.cursor()
    cursor2.execute('SELECT * FROM tipousers')
    consulta2 = cursor2.fetchall()
    return render_template('crearPersonal.html', usuario=consulta, tipousuario = consulta2,loguser=loguser )

@app.route('/crearPersonal/<string:loguser>',methods =['POST'])
def crearPersonal(loguser):
    if request.method == 'POST':
        vnombre= request.form['txtnombre']
        vmail= request.form['txtmail']
        vdomicilio= request.form['txtdomicilio']
        vdepartamento= request.form['txtdepartamento']
        vtelefono= request.form['txttelefono']
        vtipo= request.form['txttipo']
        vpass= request.form['txtpass']
        vimagen= request.form['txtimagen']
        print(vnombre,vmail,vdomicilio,vdepartamento,vtelefono, vimagen,vtipo)

        cursor=mysql.connection.cursor()
        cursor.execute('insert into users(nombre ,mail,pass, domicilio, departamento_id ,telefono, image, tipoId)values (%s,%s,%s,%s,%s,%s,%s,%s)', 
        (vnombre,vmail,vpass, vdomicilio, vdepartamento,vtelefono,vimagen,vtipo)) #%s son para las cadenas
        mysql.connection.commit()
    
    flash('Personal almacenado en la BD')
    return redirect(url_for('adminClandAux',loguser=loguser)) 

@app.route('/editarPersonal/<string:loguser>/<string:id>')
def editarPersonal(id, loguser):
    cursor= mysql.connection.cursor()
    cursor.execute('SELECT * FROM departamento INNER JOIN users ON departamento.id_departamento = users.departamento_id INNER JOIN tipousers ON users.tipoId = tipousers.idTipo where id={0}'.format(id))
    consulta= cursor.fetchall()
    cursor1=mysql.connection.cursor()
    cursor1.execute('SELECT * FROM departamento')
    consulta1 = cursor1.fetchall()
    cursor2=mysql.connection.cursor()
    cursor2.execute('SELECT * FROM tipousers')
    consulta2 = cursor2.fetchall()
    return render_template('actualizarPersonal.html', personal= consulta[0], usuario =consulta1, roles=consulta2, loguser=loguser)

@app.route('/actualizarPersonal/<string:id>/<string:loguser>',methods =['POST'])
def actualizarPersonal(id, loguser):
    if request.method=='POST':
        vnombre= request.form['txtnombre']
        vmail= request.form['txtmail']
        vdomicilio= request.form['txtdomicilio']
        vdepartamento= request.form['txtdepartamento']
        vtelefono= request.form['txttelefono']
        vtipo= request.form['txttipo']
        print(vnombre,vmail, vdomicilio, vdepartamento,vtelefono,vtipo,id)

        cursor=mysql.connection.cursor()
        cursor.execute('update users set nombre=%s ,mail=%s, domicilio=%s, departamento_id=%s ,telefono=%s ,tipoId=%s where id=%s',(vnombre,vmail, vdomicilio, vdepartamento,vtelefono,vtipo,id))
        mysql.connection.commit()

    flash('Personal se actualizo en la BD')
    return redirect(url_for('adminClandAux', loguser = loguser))


@app.route('/eliminarPersonal/<string:id>/<string:loguser>')
def eliminarPersonal(id, loguser):
    cursor= mysql.connection.cursor()
    cursor.execute('delete from users where id = {0}'.format(id))
    mysql.connection.commit()
    flash('Personal Eliminado de la base de datos')
    return redirect(url_for('adminClandAux', loguser = loguser))



##############################################################-----Departamentos---#######################################################################################
            #CONSULTAR
@app.route('/adminDepartamentos/<string:loguser>')
def AdminDepa(loguser):
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM departamento')
    consulta = cursor.fetchall()
    return render_template('adminDepartamentos.html', departamento=consulta, loguser=loguser)


            #INSERTAR
@app.route('/CrearDepartamentos/<string:loguser>')
def CrearDepa(loguser):
    return render_template('CrearDep.html', loguser= loguser)

@app.route('/insertDepas/<string:loguser>', methods=['POST'])
def insertarD(loguser):
    if request.method == ('POST'):
        depaName = request.form['nombreDepa']
        print(depaName)
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO departamento(nombre_departamento)values(%s)',[depaName])
        mysql.connection.commit()
        flash('Departamento Agregado')
        return redirect(url_for('AdminDepa', loguser= loguser))



                                #ACTUALIZAR

@app.route('/ActualizarDepartamentos/<id_departamento>/<string:loguser>')
def ActualizarDepa(id_departamento, loguser):
    cur= mysql.connection.cursor()
    cur.execute('SELECT * FROM departamento WHERE id_departamento = %s',[id_departamento])
    data=cur.fetchall()
    print(data)
    return render_template('ActualizarDep.html',departamento=data[0], loguser= loguser)

@app.route('/updateDepartamento/<id_departamento>/<string:loguser>', methods=['POST'])
def updateDepartamento(id_departamento, loguser):
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
        return redirect(url_for('AdminDepa', loguser=loguser))

        #ELIMINAR 
@app.route('/EliminarDepartamentos/<string:id_departamento>/<string:loguser>')
def EliminarDepa(id_departamento, loguser):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM departamento WHERE id_departamento =  {0}'.format(id_departamento))
    mysql.connection.commit()
    flash('Departamento Eliminado')
    return redirect(url_for('AdminDepa',loguser = loguser))

###########################################################------Tickets-----------###############################################
@app.route('/adminTickets/<string:loguser>')
def AdminTickets(loguser):
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT id_ticket, fecha, detalle,estatus, clasificacion, user_idCliente, nombre FROM ticket JOIN users ON (ticket.user_idCliente = users.id) ')
    consulta = cursor.fetchall()
    return render_template('adminTickets.html', ticket=consulta, loguser = loguser)

@app.route('/adminComentario/<id_ticket>/<string:loguser>')
def AdminComentario(id_ticket,loguser): 
    id_t=id_ticket   
    print(id_t)
    return render_template('adminComentario.html', ticket=id_t,loguser=loguser)


    #COMENTARIO PARA AUXILIAR
@app.route('/ComentarioAuxiliar/<ticket>/<string:loguser>',methods=['POST'])
def ComentarioAuxiliar(ticket,loguser):
    ticket=ticket
    cur= mysql.connection.cursor()
    cur.execute('SELECT nombre FROM users INNER JOIN ticketaux ON users.id = ticketaux.userAux_id INNER JOIN ticket ON ticketaux.ticket_idAux = ticket.id_ticket WHERE ticket.id_ticket = %s',[ticket])
    data=cur.fetchall()
    print(ticket)
    return render_template('ComentarioAuxiliar.html', ticket1=data,ticket=ticket ,loguser=loguser)

@app.route('/insertComentarioA/<ticket>/<string:loguser>',methods=['POST'])
def insertComentarioA(ticket,loguser):
  if request.method=='POST':
        #ticket_id=ticket  
        comentariosA= request.form['txtComentarioA'] 
        print(loguser)
        print(ticket)
        print(comentariosA)
        cursor=mysql.connection.cursor()
        cursor.execute('INSERT INTO comentariosAuxiliar (comentarioA , ticketAuxiliar) VALUES (%s,%s)',(comentariosA, ticket))
        mysql.connection.commit()
        return redirect(url_for('AdminTickets', loguser=loguser))

        #COMENTARIO CLIENTE
@app.route('/ComentarioCliente/<ticket>/<string:loguser>',methods=['POST'])
def ComentarioCliente(ticket,loguser):
    ticket=ticket
    cur= mysql.connection.cursor()
    cur.execute('SELECT nombre from users INNER JOIN ticket ON ticket.user_idCliente = users.id where ticket.id_ticket=%s',[ticket])
    data=cur.fetchall()
    print(ticket)
    return render_template('ComentarioCliente.html', ticket1=data,ticket=ticket,loguser=loguser)

@app.route('/insertComentarioC/<ticket>/<string:loguser>',methods=['POST'])
def insertComentarioC(ticket,loguser):
  if request.method=='POST':
        #ticket_id=ticket  
        comentarioC= request.form['txtComentarioC'] 
        print(ticket)
        print(comentarioC)
        cursor=mysql.connection.cursor()
        cursor.execute('INSERT INTO comentariosCliente(comentarioC, ticketCliente) VALUES (%s,%s)',(comentarioC, ticket))
        mysql.connection.commit()
        return redirect(url_for('AdminTickets',loguser=loguser))


        #ASIGNAR AUXILIAR

@app.route('/adminAsignar/<id_ticket>/<string:loguser>')
def adminAsignar(id_ticket,loguser):
    ticketRecived=id_ticket
    cur=mysql.connection.cursor()
    cur.execute('SELECT users.nombre, (SELECT COUNT(ticketaux.userAux_id) FROM ticketaux WHERE users.id = ticketaux.userAux_id) AS tickets_Auxiliar FROM users WHERE users.tipoId="2"')
    consultaAux=cur.fetchall()
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE tipoId = "2" ')
    consulta = cursor.fetchall()
    return render_template('adminAsignar.html', auxiliar=consulta, ticketSend=ticketRecived,ticketsAux=consultaAux,loguser=loguser)

@app.route('/asignarTicket/<ticketSend>/<string:loguser>', methods=['POST'])
def asignarTicket(ticketSend,loguser):
    if request.method=='POST':
        print(ticketSend)
        auxiliar=request.form['txtAuxiliar']
        print(auxiliar)
        cursor=mysql.connection.cursor()
        cursor.execute('INSERT INTO ticketaux (ticket_idAux, userAux_id) VALUES (%s, %s)',(ticketSend, auxiliar))
        mysql.connection.commit()
        return redirect(url_for('AdminTickets',loguser=loguser))
    
    #REPORTE
@app.route('/Reportes/<string:loguser>')
def Reportes(loguser):
    return render_template('adminReporte.html',loguser=loguser)





################################## PERFIL AUXILIAR #################################################
@app.route('/perfilAuxiliar/<string:loguser>')
def perfilAuxiliar(loguser):
    cur= mysql.connection.cursor()
    cur.execute('SELECT users.nombre, users.mail, users.domicilio, users.telefono, tipousers.tipoUsuario FROM users INNER JOIN tipousers ON users.tipoId = tipousers.idTipo WHERE users.id=%s',[loguser])
    data=cur.fetchall()
    print(data)
    return render_template('perfilAuxiliar.html', loguser = loguser,myInfo=data)


@app.route('/editarAuxiliar/<string:loguser>')
def editarAuxiliar(loguser):
    cursor= mysql.connection.cursor()
    cursor.execute('SELECT * FROM departamento INNER JOIN users ON departamento.id_departamento = users.departamento_id INNER JOIN tipousers ON users.tipoId = tipousers.idTipo WHERE id= %s ',[loguser])   
    consulta= cursor.fetchall()
    return render_template('actualizarAuxiliar.html', personal= consulta[0] , loguser=loguser )

@app.route('/actualizarAuxiliar/<string:loguser>',methods =['POST'])
def actualizarAuxiliar(loguser):
    if request.method=='POST':
        vnombre= request.form['txtnombre']
        vmail= request.form['txtmail']
        vdomicilio= request.form['txtdomicilio']
        vtelefono= request.form['txttelefono']
        print(vnombre,vmail, vdomicilio,vtelefono,loguser)

        cursor=mysql.connection.cursor()
        cursor.execute('update users set nombre=%s ,mail=%s, domicilio=%s,telefono=%s  where id=%s',(vnombre,vmail, vdomicilio,vtelefono,loguser))
        mysql.connection.commit()

    flash('Tu Perfil se actualizo en la BD')
    return redirect(url_for('perfilAuxiliar',loguser=loguser))

@app.route('/Seguimiento/<string:loguser>/<string:id_ticket>')
def Seguimiento(loguser, id_ticket):
    cur= mysql.connection.cursor()
    cur.execute('SELECT ticket.id_ticket, ticket.detalle, ticket.fecha, ticket.estatus , users.nombre, departamento.nombre_departamento FROM ticket INNER JOIN users ON ticket.user_idCliente = users.id INNER JOIN departamento ON users.departamento_id = departamento.id_departamento  WHERE ticket.id_ticket = %s',[id_ticket])
    data=cur.fetchall()
    return render_template('auxSeguimiento.html',loguser=loguser , tickets=data )

@app.route('/SeguimientoEstatus/<string:id>/<string:loguser>',methods =['POST'])
def SeguimientoEstatus(id, loguser):
    if request.method=='POST':
        estatus= request.form['txtestatus']
        print(loguser)

        cursor=mysql.connection.cursor()
        cursor.execute('update ticket set estatus=%s  where id_ticket=%s',(estatus, id))
        mysql.connection.commit()

    flash('Se ha guardado correctamente el estatus del ticket')
    return redirect(url_for('ticketsAuxiliar',loguser=loguser))



@app.route('/misTickets/<string:loguser>')
def ticketsAuxiliar(loguser):
    cur= mysql.connection.cursor()
    cur.execute('SELECT users.nombre, ticket.fecha, ticket.estatus, departamento.nombre_departamento, ticket.id_ticket, ticket.detalle FROM ticket INNER JOIN ticketaux ON ticket.id_ticket = ticketaux.ticket_idAux INNER JOIN users ON ticket.user_idCliente = users.id INNER JOIN departamento ON users.departamento_id = departamento.id_departamento WHERE ticketaux.userAux_id = %s',[loguser])
    data=cur.fetchall()
    return render_template('misTickets.html',loguser=loguser, misTickets=data)

@app.route('/ComentarioACliente/<string:loguser>/<string:id_ticket>')
def ComentarioACliente(loguser, id_ticket):
    cur= mysql.connection.cursor()
    cur.execute('SELECT users.nombre FROM ticket INNER JOIN users ON ticket.user_idCliente = users.id INNER JOIN departamento ON users.departamento_id = departamento.id_departamento  WHERE ticket.id_ticket = %s',[id_ticket])
    data=cur.fetchall()
    conexion= mysql.connection.cursor()
    conexion.execute('SELECT ticket.user_idCliente, ticket.detalle, ticket.estatus, users.nombre , comentarioscliente.comentarioC FROM ticket INNER JOIN users ON ticket.user_idCliente = users.id INNER JOIN comentarioscliente ON ticket.id_ticket = comentarioscliente.ticketCliente INNER JOIN ticketaux ON ticket.id_ticket = ticketaux.ticket_idAux WHERE ticketaux.userAux_id = %s',[loguser])
    tablas=conexion.fetchall()

    return render_template('auxComentarioC.html',loguser=loguser, data= data, ticket=id_ticket, tablas = tablas) 

@app.route('/insertAuxComentarioC/<string:ticket>/<string:loguser>',methods=['POST'])
def insertAuxComentarioC(ticket,loguser):
  if request.method=='POST':
        #ticket_id=ticket  
        comentarioC= request.form['txtComentarioC'] 
        print(loguser)
        print(ticket)
        print(comentarioC)
        cursor=mysql.connection.cursor()
        cursor.execute('INSERT INTO comentariosCliente(comentarioC, ticketCliente) VALUES (%s,%s)',(comentarioC, ticket))
        mysql.connection.commit()
        return redirect(url_for('ticketsAuxiliar', loguser=loguser))




################################## PERFIL CLIENTE #############################################3
@app.route('/perfilCliente/<string:loguser>')
def perfilCliente(loguser):

    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM departamento INNER JOIN users ON departamento.id_departamento = users.departamento_id INNER JOIN tipousers ON users.tipoId = tipousers.idTipo WHERE id= %s ', [loguser])
    consulta = cursor.fetchall()
    return render_template('perfilCliente.html', consultaAuxi = consulta , loguser = loguser)

@app.route('/editarPerfilCliente/<string:loguser>')
def editarPerfilCliente(loguser):
    cursor= mysql.connection.cursor()
    cursor.execute('SELECT * FROM departamento INNER JOIN users ON departamento.id_departamento = users.departamento_id INNER JOIN tipousers ON users.tipoId = tipousers.idTipo WHERE id= %s ', [loguser])
    consulta= cursor.fetchall()
    return render_template('actualizarPerfilCliente.html', personal= consulta[0] , loguser=loguser )

@app.route('/actualizarPerfilCliente/<string:loguser>',methods =['POST'])
def actualizarPerfilCliente(loguser):
    if request.method=='POST':
        vnombre= request.form['txtnombre']
        vmail= request.form['txtmail']
        vdomicilio= request.form['txtdomicilio']
        vtelefono= request.form['txttelefono']
        print(vnombre,vmail, vdomicilio,vtelefono,loguser)

        cursor=mysql.connection.cursor()
        cursor.execute('update users set nombre=%s ,mail=%s, domicilio=%s,telefono=%s  where id=%s',(vnombre,vmail, vdomicilio,vtelefono,loguser))
        mysql.connection.commit()

    flash('Tu Perfil se actualizo en la BD')
    return redirect(url_for('perfilCliente',loguser=loguser))

@app.route('/adminSolicitud/<string:loguser>')
def adminSolicitud(loguser):
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM ticket INNER JOIN users ON ticket.user_idCliente = users.id WHERE id= %s ', [loguser])
    consulta = cursor.fetchall()
    return render_template('clienteSolicitud.html', miSolicitud= consulta ,loguser = loguser)

@app.route('/crearSolicitud/<string:loguser>')
def crearSolicitud(loguser):
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT users.id, users.nombre,departamento.id_departamento, departamento.nombre_departamento FROM users INNER JOIN departamento ON users.departamento_id = departamento.id_departamento WHERE id= %s ', [loguser])
    consulta = cursor.fetchall()
    return render_template('crearSolicitud.html', loguser=loguser, personal =consulta)

@app.route('/insertSolicitud/<string:loguser>', methods=['POST'])
def insertarSolicitud(loguser):
    if request.method=='POST':
        print(loguser)
        
        fecha=request.form['txtfecha']
        clasificacion=request.form['txtclasificacion']
        detalles= request.form['txtdetalles'] 
        print(fecha, clasificacion, detalles)
        cursor=mysql.connection.cursor()
        cursor.execute('INSERT INTO ticket (fecha,detalle, clasificacion,user_idCliente) VALUES (%s, %s,%s, %s)',(fecha, detalles, clasificacion, loguser))
        mysql.connection.commit()
        return redirect(url_for('adminSolicitud', loguser = loguser ))

@app.route('/EliminarSolicitud/<string:loguser>/<string:idSolicitud>')
def EliminarSolicitud(loguser, idSolicitud):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM ticket  WHERE id_ticket= {0}'.format(idSolicitud))
    mysql.connection.commit()
    flash('Solicitud Eliminada')
    return redirect(url_for('adminSolicitud',loguser=loguser))

@app.route('/ComentariosAuxiliar/<string:loguser>/<string:id_ticket>')
def ComentariosAuxiliar(loguser, id_ticket):
    cur= mysql.connection.cursor()
    cur.execute('SELECT users.nombre FROM ticket INNER JOIN ticketaux ON ticket.id_ticket = ticketaux.ticket_idAux INNER JOIN users ON ticketaux.userAux_id = users.id WHERE ticket.id_ticket= %s',[id_ticket])
    data=cur.fetchall()
    conexion= mysql.connection.cursor()
    conexion.execute('SELECT users.nombre,comentariosauxiliar.comentarioA, ticket.detalle, ticket.estatus FROM ticket INNER JOIN comentariosauxiliar ON ticket.id_ticket = comentariosauxiliar.ticketAuxiliar INNER JOIN ticketaux ON ticket.id_ticket = ticketaux.ticket_idAux INNER JOIN users ON ticketaux.userAux_id = users.id WHERE ticket.user_idCliente = %s',[loguser])
    tablas=conexion.fetchall()
    return render_template('clienteComentarioA.html',loguser=loguser, data= data, ticket=id_ticket, tablas = tablas)

@app.route('/insertClienteComentarioA/<string:ticket>/<string:loguser>',methods=['POST'])
def insertClienteComentarioA(ticket,loguser):
  if request.method=='POST':
        #ticket_id=ticket  
        comentarioA= request.form['txtComentarioA'] 
        print(loguser)
        print(ticket)
        print(comentarioA)
        cursor=mysql.connection.cursor()
        cursor.execute('INSERT INTO comentariosAuxiliar(comentarioA, ticketAuxiliar) VALUES (%s,%s)',(comentarioA, ticket))
        mysql.connection.commit()
        return redirect(url_for('adminSolicitud', loguser=loguser))



#Arrancamos servidor
if __name__ == '__main__':
    app.run(port=3000,debug= True)


