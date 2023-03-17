from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import (Table, Column, Integer, String, Enum, and_)
from sqlalchemy.sql import (select, desc, asc)
from flask import Flask,render_template, request, redirect, url_for;



# Connect to MySQL Database
def connectDB():    # Cambiar datos por los propios de tu mysql
    user='root'
    password='240699'
    host='localhost'
    database='users'    # necesario tener creada una db llamada users

    # Connecta a la db
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")
    try:
        connection = engine.connect()
        return connection
    
    except Exception as e: # Si la conexion no es exitosa, se podrá cambiar
        raise e

# Create Table Users w/ (User, Passw, Name, Surname, Age, Genre)
def create_table_users():
    with connectDB() as connection: # asi nos aseguramos que siempre cierre la conexion
        metadata = MetaData() # Inicia instancia de metadata (donde se almacenan los datos de la tabla)

        # Define tabla Users 
        Users = Table('Users', metadata,
            Column('User', String(20), primary_key=True),
            Column('Password', String(30), nullable=False),
            Column('Name', String(48), nullable=False),
            Column('Surname', String(48), nullable=False),
            Column('Surname2', String(48), nullable=False),
            Column('Age', Integer, nullable=False),
            Column('Genre', Enum('H', 'D', 'NS/NC', name='sexo'), nullable=False)
        )
        
        # Comprueba si la tabla existe
        if not Users.exists(connection):
            # Si no existe, la crea
            metadata.create_all(connection)
        
# Crea nuevo User, Inserta a la tabla 
def create_user(usuario, contrasena, nombre, apellido, apellido2, edad, sexo):
    with connectDB() as connection:
        
        # Define tabla Users y autoload carga automaticamente metadata de la tabla y info de la db. No es nececario definir el esquema cada vez.
        Users = Table('Users', MetaData(), autoload=True, autoload_with=connection)

        # Inserta los datos en la tabla
        insert = Users.insert().values(User=usuario, Password=contrasena, Name=nombre, Surname=apellido, Surname2=apellido2, Age=edad, Genre=sexo)
        connection.execute(insert)
    return usuario # devuelve user (sirve para check_user y display_user_info)

        
        
        
# Check User (User & Passw  == que en la Tabla)
def check_user(usuario, contrasena): #bool
    with connectDB() as connection:
        
        # Define la tabla users, autoload para no tener que cargarla manualmente cada vez.
        Users = Table('Users', MetaData(), autoload=True, autoload_with=connection)
        
        # Busca si user y contraseña concuerdan
        selects = select([Users]).where(and_(Users.c.User == usuario, Users.c.Password == contrasena))
        
        result = connection.execute(selects).fetchone()
        
        # Si hay resultados, devuleve True
        if result is not None:
            return True
        
        # si no, devuelve False
        return False


# Display User Info (if Check User is True)
def display_user_info(username):
    with connectDB() as connection:
        # Define la tabla users
        Users = Table('Users', MetaData(), autoload=True, autoload_with=connection)

        select = Users.select().where(Users.c.User == username) # User en tabla == parametro username
        result = connection.execute(select).fetchone()

        user_info = { # devuelve esta informacion del usr
            'username': result[0],
            'password': result[1],
            'name': result[2],
            'surname': result[3],
            'surname2': result[4],
            'age': result[5],
            'gender': result[6]
        }

        return user_info



def create_admin():
    with connectDB() as connection:
        # Define la tabla users
        Users = Table('Users', MetaData(), autoload=True, autoload_with=connection)

        # Si admin user existe
        select = Users.select().where(Users.c.User == '@admin')
        result = connection.execute(select).fetchone()

        # si no existe, lo crea
        if not result:
            insert = Users.insert().values(
                User='@admin',
                Password='password',
                Name='admin', 
                Surname='surname',
                Surname2='surname2',
                Age=1,
                Genre='NS/NC'
            )
            connection.execute(insert)


        
# new_user = create_user('safuudhgj', 'esto', 'es', 'una', 'prueba', 23, 'H')

# print(display_user_info(new_user))     


# # Secuencia principal: configuración de la aplicación web ##########################################
# Instanciación de la aplicación web Flask
app = Flask(__name__)


# Flask Routes

@app.route('/')
def home():         # Iniciamos, conexion, tabla usuarios y creamos un usr @admin.
    connectDB()
    create_table_users()
    create_admin()
    
    return render_template("home.html")



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['usuario']      # datos del formulario
        password = request.form['contrasena']
        user = check_user(username, password) # Comprobamos que user este en la db.
        if user: # Si hay resultados (usr es correcto)
            user_info = display_user_info(username) 
            return render_template("login_results.html", user_info=user_info) # carga resultados login + pasamos los datos del user.
        else:
            return redirect(url_for('login')) # Si no hay user devuelve la pagina login.
    else:
        return render_template("login.html") # metodo get, devuelve la misma pagina.




@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':    # datos del formulario
        username = request.form['usuario']
        password = request.form['contrasena']
        name = request.form['nombre']
        surname = request.form['apellido']
        surname2 = request.form['apellido2']
        age = int(request.form['edad'])
        gender = request.form['sexo']
        
        # Crea nuevo user usando datos del formulario
        new_user = create_user(username, password, name, surname, surname2, age, gender)
        
        if new_user is None: # Si el usuario no puede ser creado
            return "Error creando usuario"
        
        else:   # Guardamos la info del user
            user_info = display_user_info(new_user)
            
            # cargamos resultados + datos del user
            return render_template("signin_results.html", user_info=user_info)
    else:
        return render_template("signin.html") # metodo get, devuelve la misma pagina.




# Configuración y arranque de la aplicación web
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.run(host='localhost', port=5000, debug=True)
