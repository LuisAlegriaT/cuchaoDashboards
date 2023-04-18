#importar el framework 
from colorama import Cursor
from flask import Flask, render_template, request ,Response , redirect,url_for,flash, session, make_response, send_file
from flask_mysqldb import MySQL
from flask_session import Session
from reportlab.pdfgen import canvas
import base64
from PIL import Image
import binascii


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

# Ruta protegida para el perfil de administrador
@app.before_request
def require_login():
    allowed_routes = ['log', 'login'] # Rutas permitidas sin autenticación
    if request.endpoint not in allowed_routes and 'id' not in session:
        flash('Debes iniciar sesión primero.') # Mensaje de flash para mostrar en caso de no autenticación
        return redirect(url_for('log')) # Redirigir a la página de inicio de sesión


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
                a = 'Bienvenido ' + account[1]
                flash(a)
                return redirect(url_for('adminClandAux',loguser=userlog)) # vista Admin
              
            #-----------Auxiliares
            
            if (account[0] == 2 and account[1] == usuario and account[2] == pas):
                a = 'Bienvenido ' + account[1]
                flash(a)
                return redirect(url_for('perfilAuxiliar',loguser=userlog)) # Vista Auxiliar
          
            #-----------Clientes
            if(account[0] == 3 and account[1] == usuario and account[2] == pas):
                a = 'Bienvenido ' + account[1]
                flash(a)
                return redirect(url_for('perfilCliente',loguser=userlog)) # vista clientes
        
                              
        else:
            flash('Datos incorrectos')
            return redirect(url_for('log'))
        
@app.route('/Admin/<string:id>')
def Admin(id):
    if 'id' not in session:
        return redirect(url_for('log')) # Redirigir a la página de inicio de sesión si no está autenticado
    else:
        return render_template('adminTickets.html', user=user)

@app.route('/logout')
def logout():
    session.pop('id', None) # Eliminar la variable de sesión 'id'
    return render_template('login.html') 


#Cliente y Auxiliares
@app.route('/adminClandAux/<string:loguser>')
def adminClandAux(loguser):
        cursor1=mysql.connection.cursor()
        cursor1.execute('SELECT departamento.nombre_departamento, users.id,users.nombre,users.mail,tipousers.tipoUsuario, users.image FROM departamento INNER JOIN users ON departamento.id_departamento = users.departamento_id INNER JOIN tipousers ON users.tipoId = tipousers.idTipo ')
        consulta = cursor1.fetchall()
  
        return render_template('adminClandAux.html', usuario=consulta, loguser=loguser )
        
   
    

    #BUSQUEDA DE PERSONAL

@app.route('/adminClandBusqueda/<string:loguser>', methods=['POST'])
def adminClandBusqueda(loguser):
    if request.method == 'POST':
        search= request.form['search']
        print(search)
        cursor=mysql.connection.cursor()
        
        cursor.execute("""
        SELECT * FROM departamento INNER JOIN users ON departamento.id_departamento = users.departamento_id INNER JOIN tipousers ON users.tipoId = tipousers.idTipo WHERE departamento.nombre_departamento  LIKE %s
        UNION
        SELECT * FROM departamento INNER JOIN users ON departamento.id_departamento = users.departamento_id INNER JOIN tipousers ON users.tipoId = tipousers.idTipo WHERE users.nombre LIKE %s
        UNION
        SELECT * FROM departamento INNER JOIN users ON departamento.id_departamento = users.departamento_id INNER JOIN tipousers ON users.tipoId = tipousers.idTipo WHERE tipousers.tipoUsuario LIKE %s
        UNION
        SELECT * FROM departamento INNER JOIN users ON departamento.id_departamento = users.departamento_id INNER JOIN tipousers ON users.tipoId = tipousers.idTipo WHERE users.mail LIKE %s
        UNION
        SELECT * FROM departamento INNER JOIN users ON departamento.id_departamento = users.departamento_id INNER JOIN tipousers ON users.tipoId = tipousers.idTipo WHERE users.domicilio LIKE %s
        """, ('%' + search + '%', '%' + search + '%', '%' + search + '%', '%' + search + '%', '%' + search + '%'))

        # Obtener los resultados de la búsqueda
        resultados = cursor.fetchall()

        # Renderizar una plantilla con los resultados
        return render_template('adminClandBusqueda.html', usuario=resultados,  loguser=loguser)
    else: 
        return redirect(url_for('adminClandAux',loguser=loguser)) 



        ##PERSONAL

@app.route('/loginCrear/<string:loguser>')
def loginCrear(loguser):
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM departamento')
    consulta = cursor.fetchall()
    cursor2=mysql.connection.cursor()
    cursor2.execute('SELECT * FROM tipousers')
    consulta2 = cursor2.fetchall()
    return render_template('crearPersonal.html', usuario=consulta, tipousuario = consulta2,loguser=loguser )

@app.route('/crearPersonal/<string:loguser>', methods=['POST'])
def crearPersonal(loguser):
    if request.method == 'POST':
        vnombre = request.form['txtnombre']
        vmail = request.form['txtmail']
        vdomicilio = request.form['txtdomicilio']
        vdepartamento = request.form['txtdepartamento']
        vtelefono = request.form['txttelefono']
        vtipo = request.form['txttipo']
        vpass = request.form['txtpass']
        imagen = request.files['imagen']
        imagen_bytes = imagen.read()

        cursor = mysql.connection.cursor()
        try:
            cursor.execute('INSERT INTO users(nombre, mail, pass, domicilio, departamento_id, telefono, image, tipoId) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', 
                (vnombre, vmail, vpass, vdomicilio, vdepartamento, vtelefono, imagen_bytes, vtipo))
            mysql.connection.commit()
            flash('Personal almacenado en la BD')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al insertar el personal en la BD: {str(e)}')
        finally:
            cursor.close()

    return redirect(url_for('adminClandAux', loguser=loguser))

@app.route('/editarPersonal/<string:id>/<string:loguser>')
def editarPersonal(id, loguser):
    try:
        cursor= mysql.connection.cursor()
        cursor.execute('SELECT * FROM departamento INNER JOIN users ON departamento.id_departamento = users.departamento_id INNER JOIN tipousers ON users.tipoId = tipousers.idTipo where id={0}'.format(id))
        consulta= cursor.fetchall()
        cursor1=mysql.connection.cursor()
        cursor1.execute('SELECT * FROM departamento')
        consulta1 = cursor1.fetchall()
        cursor2=mysql.connection.cursor()
        cursor2.execute('SELECT * FROM tipousers')
        consulta2 = cursor2.fetchall()

        
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT image FROM users WHERE id=%s", (id,))
        imagen_actual = cursor.fetchone()[0]


        if imagen_actual:
            # Obtener la imagen en formato binario desde la base de datos
            imagen_binario = imagen_actual
            # Codificar la imagen en base64
            imagen_base64 = base64.b64encode(imagen_binario).decode('utf-8')

            # Pasar la información de la imagen a la plantilla HTML
            return render_template('actualizarPersonal.html', personal= consulta[0], usuario =consulta1, roles=consulta2, loguser=loguser, imagen_base64=imagen_base64)

        else:
            # Manejar caso si la imagen no existe
            return 'Imagen no encontrada', 404
    except Exception as e:
        return str(e), 500


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

@app.route('/adminPersonalImagen/<string:id>/<string:loguser>')
def adminPersonalImagen(id, loguser):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT image FROM users WHERE id=%s", (id,))
    imagen_actual = cursor.fetchone()[0]


    if imagen_actual:
            # Obtener la imagen en formato binario desde la base de datos
        imagen_binario = imagen_actual
            # Codificar la imagen en base64
        imagen_base64 = base64.b64encode(imagen_binario).decode('utf-8')
        return render_template('adminPersonalImagen.html', loguser=loguser, id =id, imagen_base64=imagen_base64)

    
@app.route('/actualizarImagenPersonal/<string:id>/<string:loguser>',methods =['POST'])
def actualizarImagenPersonal(id, loguser):
   
        # Obtener la imagen actual de la base de datos
        cursor = mysql.connection.cursor()

        # Actualizar la imagen en la base de datos
        nueva_imagen = request.files['nueva_imagen']
        cursor.execute("UPDATE users SET image=%s WHERE id=%s", (nueva_imagen.read(), id))
        mysql.connection.commit()

        # Mostrar una respuesta al usuario
        flash( 'Imagen actualizada correctamente')
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

        #BUSQUEDA DE DEPARTAMENTOS
@app.route('/adminDepartamentosBusqueda/<string:loguser>', methods=['POST'])
def adminDepartamentosBusqueda(loguser):
    if request.method == 'POST':
        buscar= request.form['buscar']
        print(buscar)
        cursor=mysql.connection.cursor()
        
        cursor.execute("""SELECT * FROM departamento WHERE nombre_departamento  LIKE %s
        UNION 
        SELECT * FROM departamento WHERE id_departamento  LIKE %s""",('%' + buscar + '%', '%' + buscar + '%'))

        # Obtener los resultados de la búsqueda
        resultados = cursor.fetchall()

        # Renderizar una plantilla con los resultados
        return render_template('adminDepartamentosBusqueda.html', departamento=resultados,  loguser=loguser)
    else: 
        return redirect(url_for('AdminDepa',loguser=loguser)) 



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

    #BUSCAR TICKET
@app.route('/adminTicketsBusqueda/<string:loguser>', methods=['POST'])
def adminTicketsBusqueda(loguser):
    if request.method == 'POST':
        buscar= request.form['buscar']
        print(buscar)
        cursor=mysql.connection.cursor()
        
        cursor.execute("""
        SELECT * FROM ticket JOIN users ON (ticket.user_idCliente = users.id) WHERE ticket.fecha LIKE %s
        UNION 
        SELECT * FROM ticket JOIN users ON (ticket.user_idCliente = users.id) WHERE ticket.detalle LIKE %s
        UNION
        SELECT * FROM ticket JOIN users ON (ticket.user_idCliente = users.id) WHERE ticket.estatus LIKE %s
        UNION
        SELECT * FROM ticket JOIN users ON (ticket.user_idCliente = users.id) WHERE ticket.clasificacion LIKE %s
        UNION
        SELECT * FROM ticket JOIN users ON (ticket.user_idCliente = users.id) WHERE users.nombre LIKE %s
        """,('%' + buscar + '%', '%' + buscar + '%', '%' + buscar + '%','%' + buscar + '%', '%' + buscar + '%'))

        # Obtener los resultados de la búsqueda
        resultados = cursor.fetchall()

        # Renderizar una plantilla con los resultados
        return render_template('adminTicketsBusqueda.html', ticket=resultados,  loguser=loguser)
    else: 
        return redirect(url_for('AdminTickets',loguser=loguser)) 


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
    cursor1=mysql.connection.cursor()
    cursor1.execute('SELECT estatus FROM ticket WHERE id_ticket = %s',(ticketSend))
    mysql.connection.commit()
    cursores = cursor1.fetchone()
    print(cursores[0])

    if ( cursores[0] == "Completado" or cursores[0] == "Nunca solucionado" or cursores[0] == "Cancelado" or cursores[0] == "Asignado" or cursores[0] == "Proceso"  ):
        a = " Tu ticket no puede ser modificado porque ya esta  "+ cursores[0]
                
        flash(a)
        return redirect(url_for('AdminTickets',loguser=loguser))
    else :
        estatus= 'Asignado'
        status=mysql.connection.cursor()
        status.execute('update ticket set estatus=%s  where id_ticket=%s',(estatus, ticketSend))
        mysql.connection.commit()
        if request.method=='POST':
            print(ticketSend)
            auxiliar=request.form['txtAuxiliar']
            print(auxiliar)
            cursor=mysql.connection.cursor()
            cursor.execute('INSERT INTO ticketaux (ticket_idAux, userAux_id) VALUES (%s, %s)',(ticketSend, auxiliar))
            mysql.connection.commit()
        flash('Tu ticket ya fue asignado')   
        return redirect(url_for('adminAsignar',id_ticket= ticketSend,loguser=loguser))
    
    
    #REPORTE
@app.route('/AdminReportes/<string:loguser>')
def AdminReportes(loguser):
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM ticket INNER JOIN users ON ticket.user_idCliente = users.id ')
    reporte = cursor.fetchall()
    return render_template('adminReporte.html',loguser=loguser , reporte = reporte)


@app.route('/adminGenerarReporte')
def adminGenerarReporte():
    # Crear el archivo PDF
       
    reporte_path = 'static/reportes/adminReporte.pdf'
   
    # Retornar el archivo generado utilizando Flask send_file
    return send_file(reporte_path, as_attachment=True)



################################## PERFIL AUXILIAR #################################################
@app.route('/perfilAuxiliar/<string:loguser>')
def perfilAuxiliar(loguser):
    
    cur= mysql.connection.cursor()
    cur.execute('SELECT users.nombre, users.mail, users.domicilio, users.telefono, tipousers.tipoUsuario FROM users INNER JOIN tipousers ON users.tipoId = tipousers.idTipo WHERE users.id=%s',[loguser])
    data=cur.fetchall()
    print(data)
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT image FROM users WHERE id=%s", (loguser,))
    imagen_actual = cursor.fetchone()[0]


    if imagen_actual:
            # Obtener la imagen en formato binario desde la base de datos
        imagen_binario = imagen_actual
            # Codificar la imagen en base64
        imagen_base64 = base64.b64encode(imagen_binario).decode('utf-8')

            # Pasar la información de la imagen a la plantilla HTML
        return render_template('perfilAuxiliar.html', loguser=loguser, myInfo=data, imagen_base64=imagen_base64)
    else:
            # Manejar caso si la imagen no existe
        return 'Imagen no encontrada', 404  


@app.route('/editarAuxiliar/<string:loguser>')
def editarAuxiliar(loguser):
    try:
        cursor= mysql.connection.cursor()
        cursor.execute('SELECT * FROM departamento INNER JOIN users ON departamento.id_departamento = users.departamento_id INNER JOIN tipousers ON users.tipoId = tipousers.idTipo WHERE id= %s ',[loguser])   
        consulta= cursor.fetchall()
        cursor1 = mysql.connection.cursor()
        cursor1.execute("SELECT image FROM users WHERE id=%s", (loguser,))
        imagen_actual = cursor1.fetchone()[0]


        if imagen_actual:
            # Obtener la imagen en formato binario desde la base de datos
            imagen_binario = imagen_actual
            # Codificar la imagen en base64
            imagen_base64 = base64.b64encode(imagen_binario).decode('utf-8')

            # Pasar la información de la imagen a la plantilla HTML
            return render_template('actualizarAuxiliar.html', personal= consulta[0] , loguser=loguser , imagen_base64=imagen_base64)
        else:
            # Manejar caso si la imagen no existe
            return 'Imagen no encontrada', 404
    except Exception as e:
        return str(e), 500
   

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


@app.route('/auxiliarActualizarImagen/<string:loguser>')
def auxiliarActualizarImagen( loguser):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT image FROM users WHERE id=%s", (loguser,))
    imagen_actual = cursor.fetchone()[0]


    if imagen_actual:
            # Obtener la imagen en formato binario desde la base de datos
        imagen_binario = imagen_actual
            # Codificar la imagen en base64
        imagen_base64 = base64.b64encode(imagen_binario).decode('utf-8')
        return render_template('auxiliarEditarImagen.html', loguser=loguser, imagen_base64=imagen_base64)

    
@app.route('/auxiliarEditarImagen/<string:loguser>',methods =['POST'])
def auxiliarEditarImagen( loguser):
   
        # Obtener la imagen actual de la base de datos
        cursor = mysql.connection.cursor()

        # Actualizar la imagen en la base de datos
        nueva_imagen = request.files['nueva_imagen']
        cursor.execute("UPDATE users SET image=%s WHERE id=%s", (nueva_imagen.read(), loguser))
        mysql.connection.commit()

        # Mostrar una respuesta al usuario
        flash( 'Imagen actualizada correctamente')
        return redirect(url_for('editarAuxiliar', loguser = loguser))


@app.route('/Seguimiento/<string:loguser>/<string:id_ticket>')
def Seguimiento(loguser, id_ticket):
    cur= mysql.connection.cursor()
    cur.execute('SELECT ticket.id_ticket, ticket.detalle, ticket.fecha, ticket.estatus , users.nombre, departamento.nombre_departamento FROM ticket INNER JOIN users ON ticket.user_idCliente = users.id INNER JOIN departamento ON users.departamento_id = departamento.id_departamento  WHERE ticket.id_ticket = %s',[id_ticket])
    data=cur.fetchall()
    return render_template('auxSeguimiento.html',loguser=loguser , tickets=data )

@app.route('/SeguimientoEstatus/<string:id>/<string:loguser>',methods =['POST'])
def SeguimientoEstatus(id, loguser):
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT estatus FROM ticket WHERE id_ticket = %s',(id))
    mysql.connection.commit()
    cursores = cursor.fetchone()
    print(cursor)
    print(cursores[0])
    if ( cursores[0] == "Completado" or cursores[0] == "Nunca solucionado" or cursores[0] == "Cancelado" ):
        a = " Tu ticket no puede ser modificado porque ya esta  "+ cursores[0]
        
        flash(a)
    else:
        
        estatus= request.form['txtestatus']
        print(loguser)

        cursor=mysql.connection.cursor()
        cursor.execute('update ticket set estatus=%s  where id_ticket=%s',(estatus, id))
        mysql.connection.commit()

        flash('Se ha guardado correctamente el estatus del ticket')
    return redirect(url_for('ticketsAuxiliar',loguser=loguser))

    
        #TICKETS


@app.route('/misTickets/<string:loguser>')
def ticketsAuxiliar(loguser):
    cur= mysql.connection.cursor()
    cur.execute('SELECT users.nombre, ticket.fecha, ticket.estatus, departamento.nombre_departamento, ticket.id_ticket, ticket.detalle FROM ticket INNER JOIN ticketaux ON ticket.id_ticket = ticketaux.ticket_idAux INNER JOIN users ON ticket.user_idCliente = users.id INNER JOIN departamento ON users.departamento_id = departamento.id_departamento WHERE ticketaux.userAux_id = %s',[loguser])
    data=cur.fetchall()
    return render_template('misTickets.html',loguser=loguser, misTickets=data)

        #BUSQUEDA DE TICKETS


@app.route('/auxiliarTicketsBusqueda/<string:loguser>', methods=['POST'])
def auxiliarTicketsBusqueda(loguser):
    if request.method == 'POST':
        buscar= request.form['buscar']
        print(buscar)
        cursor=mysql.connection.cursor()
        
        cursor.execute("""
        SELECT * FROM ticket INNER JOIN ticketaux ON ticket.id_ticket = ticketaux.ticket_idAux INNER JOIN users ON ticket.user_idCliente = users.id INNER JOIN departamento ON users.departamento_id = departamento.id_departamento WHERE ticket.fecha LIKE %s 
        AND ticketaux.userAux_id = %s
        
        UNION 
        SELECT *  FROM ticket INNER JOIN ticketaux ON ticket.id_ticket = ticketaux.ticket_idAux INNER JOIN users ON ticket.user_idCliente = users.id INNER JOIN departamento ON users.departamento_id = departamento.id_departamento WHERE ticket.detalle LIKE %s
        AND ticketaux.userAux_id = %s
        UNION
        SELECT * FROM ticket INNER JOIN ticketaux ON ticket.id_ticket = ticketaux.ticket_idAux INNER JOIN users ON ticket.user_idCliente = users.id INNER JOIN departamento ON users.departamento_id = departamento.id_departamento WHERE ticket.estatus LIKE %s
        AND ticketaux.userAux_id = %s
        UNION
        SELECT *  FROM ticket INNER JOIN ticketaux ON ticket.id_ticket = ticketaux.ticket_idAux INNER JOIN users ON ticket.user_idCliente = users.id INNER JOIN departamento ON users.departamento_id = departamento.id_departamento WHERE ticket.clasificacion LIKE %s
        AND ticketaux.userAux_id = %s
        UNION
        SELECT * FROM ticket INNER JOIN ticketaux ON ticket.id_ticket = ticketaux.ticket_idAux INNER JOIN users ON ticket.user_idCliente = users.id INNER JOIN departamento ON users.departamento_id = departamento.id_departamento  WHERE users.nombre LIKE %s  
        AND ticketaux.userAux_id = %s
        UNION
        SELECT * FROM ticket INNER JOIN ticketaux ON ticket.id_ticket = ticketaux.ticket_idAux INNER JOIN users ON ticket.user_idCliente = users.id INNER JOIN departamento ON users.departamento_id = departamento.id_departamento  WHERE departamento.nombre_departamento LIKE %s 
        AND ticketaux.userAux_id = %s
        """,('%' + buscar + '%', loguser , '%' + buscar + '%',loguser , '%' + buscar + '%', loguser,'%' + buscar + '%', loguser, '%' + buscar + '%', loguser , '%' + buscar + '%', loguser  ))

        # Obtener los resultados de la búsqueda
        resultados = cursor.fetchall()

        # Renderizar una plantilla con los resultados
        return render_template('auxiliarTicketsBusqueda.html', misTickets=resultados,  loguser=loguser)
    else: 
        return redirect(url_for('ticketsAuxiliar',loguser=loguser))

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
    
    cursor1=mysql.connection.cursor()
    cursor1.execute('SELECT * FROM departamento INNER JOIN users ON departamento.id_departamento = users.departamento_id INNER JOIN tipousers ON users.tipoId = tipousers.idTipo WHERE id= %s ', [loguser])
    consulta = cursor1.fetchall()
    cursor = mysql.connection.cursor()
            # Obtener información de la imagen desde la base de datos
        
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT image FROM users WHERE id=%s", (loguser,))
    imagen_actual = cursor.fetchone()[0]


    if imagen_actual:
            # Obtener la imagen en formato binario desde la base de datos
        imagen_binario = imagen_actual
            # Codificar la imagen en base64
        imagen_base64 = base64.b64encode(imagen_binario).decode('utf-8')

            # Pasar la información de la imagen a la plantilla HTML
        return render_template('perfilCliente.html', loguser=loguser, consultaAuxi = consulta, imagen_base64=imagen_base64)

    else:
            # Manejar caso si la imagen no existe
        return 'Imagen no encontrada', 404  

           
    
    
@app.route('/editarPerfilCliente/<string:loguser>')
def editarPerfilCliente(loguser):
    cursor= mysql.connection.cursor()
    cursor.execute('SELECT * FROM departamento INNER JOIN users ON departamento.id_departamento = users.departamento_id INNER JOIN tipousers ON users.tipoId = tipousers.idTipo WHERE id= %s ', [loguser])
    consulta= cursor.fetchall()
    cursor1 = mysql.connection.cursor()
    cursor1.execute("SELECT image FROM users WHERE id=%s", (loguser,))
    imagen_actual = cursor1.fetchone()[0]


    if imagen_actual:
            # Obtener la imagen en formato binario desde la base de datos
        imagen_binario = imagen_actual
            # Codificar la imagen en base64
        imagen_base64 = base64.b64encode(imagen_binario).decode('utf-8')

            # Pasar la información de la imagen a la plantilla HTML
        return render_template('actualizarPerfilCliente.html', personal= consulta[0] , loguser=loguser , imagen_base64=imagen_base64)
    else:
            # Manejar caso si la imagen no existe
        return 'Imagen no encontrada', 404
   

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

@app.route('/clienteActualizarImagen/<string:loguser>')
def clienteActualizarImagen( loguser):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT image FROM users WHERE id=%s", (loguser,))
    imagen_actual = cursor.fetchone()[0]


    if imagen_actual:
            # Obtener la imagen en formato binario desde la base de datos
        imagen_binario = imagen_actual
            # Codificar la imagen en base64
        imagen_base64 = base64.b64encode(imagen_binario).decode('utf-8')
        return render_template('ClienteEditarImagen.html', loguser=loguser, imagen_base64=imagen_base64)

    
@app.route('/ClienteEditarImagen/<string:loguser>',methods =['POST'])
def ClienteEditarImagen( loguser):
   
        # Obtener la imagen actual de la base de datos
        cursor = mysql.connection.cursor()

        # Actualizar la imagen en la base de datos
        nueva_imagen = request.files['nueva_imagen']
        cursor.execute("UPDATE users SET image=%s WHERE id=%s", (nueva_imagen.read(), loguser))
        mysql.connection.commit()

        # Mostrar una respuesta al usuario
        flash( 'Imagen actualizada correctamente')
        return redirect(url_for('editarPerfilCliente', loguser = loguser))

        #SOLICITUD

@app.route('/clienteSolicitud/<string:loguser>')
def clienteSolicitud(loguser):
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM ticket INNER JOIN users ON ticket.user_idCliente = users.id WHERE id= %s ', [loguser])
    consulta = cursor.fetchall()
    return render_template('clienteSolicitud.html', miSolicitud= consulta ,loguser = loguser)

        #BUSQUEDA DE SOLICITUD

@app.route('/clienteSolicitudBusqueda/<string:loguser>', methods=['POST'])
def clienteSolicitudBusqueda(loguser):
    if request.method == 'POST':
        buscar= request.form['buscar']
        print(buscar)
        cursor=mysql.connection.cursor()
        print(loguser)
        
        cursor.execute("""
        SELECT * FROM ticket JOIN users ON (ticket.user_idCliente = users.id) WHERE ticket.fecha LIKE %s
        AND ticket.user_idCliente = %s
        UNION 
        SELECT * FROM ticket JOIN users ON (ticket.user_idCliente = users.id) WHERE ticket.detalle LIKE %s
        AND ticket.user_idCliente = %s 
        UNION
        SELECT * FROM ticket JOIN users ON (ticket.user_idCliente = users.id) WHERE ticket.estatus LIKE %s
        AND ticket.user_idCliente = %s         
        """,('%' + buscar + '%', loguser , '%' + buscar + '%',loguser , '%' + buscar + '%', loguser))

        # Obtener los resultados de la búsqueda
        resultados = cursor.fetchall()

        # Renderizar una plantilla con los resultados
        return render_template('clienteSolicitudBusqueda.html', miSolicitud=resultados,  loguser=loguser)
    else: 
        return redirect(url_for('clienteSolicitud',loguser=loguser))



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
        return redirect(url_for('clienteSolicitud', loguser = loguser ))

@app.route('/EliminarSolicitud/<string:loguser>/<string:idSolicitud>')
def EliminarSolicitud(loguser, idSolicitud):
    estatus=mysql.connection.cursor()
    estatus.execute('SELECT estatus FROM ticket WHERE id_ticket = %s',(idSolicitud))
    mysql.connection.commit()
    status = estatus.fetchone()
    print(estatus)
    print(status[0])
    if (status[0] == "Proceso" or status[0] == "Asignado" or status[0] == "Completado" or status[0] == "Nunca solucionado" or status[0] == "Cancelado" ):
        a = " Tu ticket no puede ser cancelado porque ya esta en "+ status[0]
        
        flash(a)
    else:
        valor = "Cancelado"  
        cursor=mysql.connection.cursor()
        cursor.execute('UPDATE ticket SET estatus = %s WHERE ticket.id_ticket = %s',(valor,idSolicitud))
        mysql.connection.commit()
        flash('Tu Ticket fue cancelado')
    return redirect(url_for('clienteSolicitud',loguser=loguser))

@app.route('/NuncaSolicitud/<string:loguser>/<string:idSolicitud>')
def NuncaSolicitud(loguser, idSolicitud):
    estatus=mysql.connection.cursor()
    estatus.execute('SELECT estatus FROM ticket WHERE id_ticket = %s',(idSolicitud))
    mysql.connection.commit()
    status = estatus.fetchone()
    print(estatus)
    print(status[0])
    if (status[0] == "Nunca solucionado" or status[0] == "Cancelado" ):
        a = " Tu ticket no puede ser modificado porque ya esta en "+ status[0]
        
        flash(a)
    else:
        valor = "Nunca solucionado"  
        cursor=mysql.connection.cursor()
        cursor.execute('UPDATE ticket SET estatus = %s WHERE ticket.id_ticket = %s',(valor,idSolicitud))
        mysql.connection.commit()
        flash('Tu Ticket nunca fue solucionado')
    return redirect(url_for('clienteSolicitud',loguser=loguser))


        

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
        return redirect(url_for('clienteSolicitud', loguser=loguser))



#Arrancamos servidor
if __name__ == '__main__':
    app.run(port=3000,debug= True)


