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
app.config['MYSQL_DB']= 'BDMacuin'
mysql= MySQL(app)
app.secret_key='mysecretkey'

@app.route('/')
def login():
    return render_template('adminClandAux.html')

#Arrancamos servidor
if __name__ == '__main__':
    app.run(port=3000,debug= True)


