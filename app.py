from flask import Flask, request, render_template, redirect, url_for, session, flash
import mysql.connector, datetime
from werkzeug.utils import secure_filename
import os
import csv
from flask import send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__)


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'Aeropuerto'  
}



UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/')
def index():
    return render_template('login.html')





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT id, nombre, correo, contraseña, rol FROM usuarios WHERE correo = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user[3], password):  
            session['user_id'] = user[0]
            session['name'] = user[1]
            session['role'] = user[4]

            if user[4] == 'administrativo': 
                return redirect(url_for('admin_dashboard'))
            elif user[4] == 'transportador':
                return redirect(url_for('transport_dashboard'))
        else:
            flash("Correo o contraseña incorrectos", "error")  

    return render_template("login.html") 

    
@app.route('/admin_dashboard.html')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))  

 
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

  
    cursor.execute("SELECT id, nombre, correo, rol, contraseña FROM usuarios")
    users = cursor.fetchall()

 
    transportadores = [user for user in users if user[3] == 'transportador']


    cursor.close()
    conn.close()

    return render_template(
        'admin_dashboard.html',
        name=session.get('name', 'Administrador'),
        users=users,
        transportadores=transportadores,
    )


@app.route('/update_user', methods=['POST'])
def update_user():
    if 'user_id' not in session:
        return redirect(url_for('index'))  

    user_id = request.form['user_id']
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if password:  # Si se ingresó una nueva contraseña, se cifra
        hashed_password = generate_password_hash(password)
        cursor.execute("""
            UPDATE usuarios
            SET nombre = %s, correo = %s, contraseña = %s, rol = %s
            WHERE id = %s
        """, (name, email, hashed_password, role, user_id))
    else:  # Si no se cambia la contraseña, se actualizan solo los otros campos
        cursor.execute("""
            UPDATE usuarios
            SET nombre = %s, correo = %s, rol = %s
            WHERE id = %s
        """, (name, email, role, user_id))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('admin_dashboard'))



@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))  

    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))

   
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('admin_dashboard'))  





@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if 'user_id' not in session:
        return redirect(url_for('index'))  

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT id, nombre, correo, rol FROM usuarios")  # No obtener contraseñas
        users = cursor.fetchall()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        hashed_password = generate_password_hash(password)  # Cifra la contraseña

        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, contraseña, rol)
            VALUES (%s, %s, %s, %s)
        """, (name, email, hashed_password, role))

        conn.commit()
        return redirect(url_for('create_user')) 

    cursor.close()
    conn.close()

    return render_template(
        'create_user.html',
        name=session.get('name', 'Administrador'),
        users=users,
    )







@app.route('/create_vehicle', methods=['GET', 'POST'])
def create_vehicle():
    if 'user_id' not in session or session['role'] != 'administrativo':
        return redirect(url_for('index'))  

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if request.method == 'POST':
        # Capturar datos del formulario
        modelo = request.form['modelo']
        placa = request.form['placa']
        fecha_recogida = request.form['fecha_recogida']
        hora_recogida = request.form['hora_recogida']
        estado = 'Recogida'
        cliente_nombre = request.form['cliente_nombre']
        cliente_telefono = request.form['cliente_telefono']
        fecha_entrega = request.form['fecha_entrega']
        hora_entrega = request.form['hora_entrega']
        precio = request.form['precio']
        numero_reserva = request.form['numero_reserva']

        # Insertar en la base de datos
        cursor.execute("""
            INSERT INTO vehiculos (modelo, placa, fecha_recogida, hora_recogida, estado, cliente_nombre, cliente_telefono, fecha_entrega, hora_entrega, precio, numero_reserva)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (modelo, placa, fecha_recogida, hora_recogida, estado, cliente_nombre, cliente_telefono,  fecha_entrega, hora_entrega, precio, numero_reserva))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('ver_vehiculos'))

    return render_template('create_vehicle.html', name=session.get('name', 'Administrador'))







@app.route('/update_vehicle/<int:vehicle_id>', methods=['POST'])
def update_vehicle(vehicle_id):
    if 'user_id' not in session or session['role'] not in ['administrativo', 'transportador']:
        return redirect(url_for('index'))

    new_status = request.form['estado']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE vehiculos
        SET estado = %s
        WHERE id = %s
    """, (new_status, vehicle_id))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('admin_dashboard' if session['role'] == 'administrativo' else 'transport_dashboard'))




from datetime import datetime

@app.route('/ver_vehiculos')
def ver_vehiculos():
    if 'user_id' not in session:
        return redirect(url_for('index'))  
    
   
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    
    cursor.execute("""
        SELECT v.id, v.modelo, v.fecha_recogida, v.hora_recogida, v.fecha_entrega, v.hora_entrega, v.cliente_nombre, v.cliente_telefono, v.cliente_correo,
               v.comentarios, v.descripcion, v.placa, v.ubicacion, v.estado, v.precio , numero_vuelo, v.numero_reserva,
               ue.nombre AS usuario_entrega_nombre, ur.nombre AS usuario_recogida_nombre
        FROM vehiculos v
        LEFT JOIN usuarios ue ON v.usuario_entrega = ue.id
        LEFT JOIN usuarios ur ON v.usuario_recogida = ur.id
    """)
    vehicles = cursor.fetchall()
    
   
    today = datetime.today().date()

    for vehicle in vehicles:
        updated_state = None
        current_state = vehicle['estado'].lower()

       
        if current_state in ['en recogida', 'en entrega', 'entregado']:
            continue

      
        if vehicle['fecha_recogida'] and vehicle['fecha_recogida'] == today and current_state != 'recogido':
            updated_state = "Recogida"

       
        elif vehicle['fecha_entrega'] and vehicle['fecha_entrega'] == today and current_state == 'recogido':
            updated_state = "Entrega"
        
        elif vehicle['fecha_entrega'] and vehicle['fecha_entrega'] == today and current_state == 'recogida':
            updated_state = "Entrega"
        

        
      
        elif vehicle['fecha_entrega'] and vehicle['fecha_entrega'] < today and current_state != 'entregado':
            updated_state = "Entregado"

      
        if updated_state:
            vehicle['estado'] = updated_state

   
    conn.commit()
    
   
    cursor.close()
    conn.close()
    
    return render_template(
        'ver_vehiculos.html',
        vehicles=vehicles,
        name=session.get('name', 'Administrador'),
    )





@app.route('/reporte_transportadores', methods=['GET'])
def reporte_transportadores():
 
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()


    cursor.execute("SELECT id, nombre, correo, rol FROM usuarios WHERE rol = 'transportador'")
    transportadores = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'reporte_transportadores.html',
        name=session.get('name', 'Administrador'),
        transportadores=transportadores,
    )


@app.route('/reporte_transportador/<int:transportador_id>', methods=['GET', 'POST'])
def reporte_transportador(transportador_id):

    filtro = request.form.get('filtro', 'mensual')  
    fecha = request.form.get('fecha', datetime.now().strftime('%Y-%m'))  

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

 
    if filtro == 'diario':
        fecha_inicio = f"{fecha} 00:00:00"
        fecha_fin = f"{fecha} 23:59:59"
    else: 
        año, mes = fecha.split('-')
        fecha_inicio = f"{año}-{mes}-01 00:00:00"

        if mes == '01':  
            fecha_fin = f"{año}-01-31 23:59:59"
        elif mes == '02':  
            fecha_fin = f"{año}-02-28 23:59:59"  
        elif mes == '03':  
            fecha_fin = f"{año}-03-31 23:59:59"
        elif mes == '04': 
            fecha_fin = f"{año}-04-30 23:59:59"
        elif mes == '05': 
            fecha_fin = f"{año}-05-31 23:59:59"
        elif mes == '06':  
            fecha_fin = f"{año}-06-30 23:59:59"
        elif mes == '07': 
            fecha_fin = f"{año}-07-31 23:59:59"
        elif mes == '08': 
            fecha_fin = f"{año}-08-31 23:59:59"
        elif mes == '09':  
            fecha_fin = f"{año}-09-30 23:59:59"
        elif mes == '10':  
            fecha_fin = f"{año}-10-31 23:59:59"
        elif mes == '11':  
            fecha_fin = f"{año}-11-30 23:59:59"
        else:  
            fecha_fin = f"{año}-12-31 23:59:59"

  
    cursor.execute("""
        SELECT v.id, v.modelo, v.placa, v.estado, v.fecha_recogida, v.fecha_entrega, v.usuario_recogida, v.usuario_entrega
        FROM vehiculos v
        WHERE (v.usuario_recogida = %s OR v.usuario_entrega = %s)
        AND ((v.fecha_recogida BETWEEN %s AND %s)
        OR (v.fecha_entrega BETWEEN %s AND %s))
    """, (transportador_id, transportador_id, fecha_inicio, fecha_fin, fecha_inicio, fecha_fin))

    vehiculos = cursor.fetchall()


    cursor.execute("SELECT nombre FROM usuarios WHERE id = %s", (transportador_id,))
    transportador_nombre = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return render_template(
        'reporte_transportador.html',
        transportador_nombre=transportador_nombre,
        vehiculos=vehiculos,
        name=session.get('name', 'Administrador'),
        filtro=filtro,
        fecha=fecha,
    )






from datetime import datetime

@app.route('/transport_dashboard', methods=['GET', 'POST'])
def transport_dashboard():
    if 'user_id' not in session or session['role'] != 'transportador':
        return redirect(url_for('index'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    today = datetime.today().date()
    cursor.execute("""
        SELECT id, modelo, fecha_recogida, hora_recogida, fecha_entrega, hora_entrega, 
                cliente_nombre, cliente_telefono, cliente_correo, comentarios, numero_vuelo, numero_reserva,
               descripcion, placa, ubicacion, estado 
        FROM vehiculos
    """)
    vehicles = cursor.fetchall()



    for vehicle in vehicles:
        updated_state = None
        current_state = vehicle['estado'].lower()


        if current_state in ['en recogida', 'en entrega', 'entregado']:
            continue


        if vehicle['fecha_recogida'] and vehicle['fecha_recogida'] == today and current_state != 'recogido':
            updated_state = "Recogida"

    
        elif vehicle['fecha_entrega'] and vehicle['fecha_entrega'] == today and current_state == 'recogido':
            updated_state = "Entrega"
        
        elif vehicle['fecha_entrega'] and vehicle['fecha_entrega'] == today and current_state == 'recogida':
            updated_state = "Entrega"
        
 
        elif vehicle['fecha_entrega'] and vehicle['fecha_entrega'] < today and current_state != 'entregado':
            updated_state = "Entregado"

   
        if updated_state:
            vehicle['estado'] = updated_state


  
        if updated_state:
            vehicle['estado'] = updated_state
            cursor.execute(
                "UPDATE vehiculos SET estado = %s WHERE id = %s",
                (updated_state, vehicle['id'])
            )

    if request.method == 'POST':
        vehiculos_id = request.form.get('vehiculos_id')
        user_id = session.get('user_id')  


        print(f"ID del Vehiculo: {vehiculos_id}, User ID: {user_id}")

        if vehiculos_id and user_id:

            cursor.execute("""
                SELECT estado 
                FROM vehiculos
                WHERE id = %s
            """, (vehiculos_id,))

            current_state = cursor.fetchone()

            if current_state:
                current_state = current_state['estado'].lower()

   
                if current_state == 'recogida':
                    new_state = 'en recogida'
                elif current_state == 'entrega':
                    new_state = 'en entrega'
                else:
                    new_state = 'en proceso'

     
                cursor.execute("""
                    UPDATE vehiculos
                    SET estado = %s, usuario_entrega = %s
                    WHERE id = %s
                """, (new_state, user_id, vehiculos_id))
                conn.commit()

                print(f"Vehículo {vehiculos_id} actualizado a estado: {new_state}.")
            else:
                print("No se encontró el vehículo en la base de datos.")


            return redirect(url_for('transport_dashboard'))


    today = datetime.today().date().strftime('%Y-%m-%d')


    query = """
        SELECT id, modelo, fecha_recogida, hora_recogida, fecha_entrega, hora_entrega, 
                cliente_nombre, cliente_telefono, cliente_correo, numero_vuelo, numero_reserva,
               comentarios, descripcion, placa, ubicacion, estado
        FROM vehiculos
        WHERE estado IN ('recogida', 'Entrega')
        AND (fecha_recogida = %s OR fecha_entrega = %s)
    """
    cursor.execute(query, (today, today))
    vehiculos = cursor.fetchall()


    vehiculos.sort(key=lambda x: (x['hora_recogida'] if x['estado'].lower() == 'recogida' 
                              else x['hora_entrega']), reverse=False)


    for vehiculo in vehiculos:
        if vehiculo['estado'].lower() == 'recogida':
            vehiculo['informacion_relevante'] = {
                'titulo': 'Recogida',
                'fecha': vehiculo['fecha_recogida'],
                'hora': vehiculo['hora_recogida']
            }
        elif vehiculo['estado'].lower() == 'entrega':
            vehiculo['informacion_relevante'] = {
                'titulo': 'Entrega',
                'fecha': vehiculo['fecha_entrega'],
                'hora': vehiculo['hora_entrega']
            }
        else:
            vehiculo['informacion_relevante'] = {
                'titulo': 'Estado no especificado',
                'fecha': None,
                'hora': None
            }

    cursor.close()
    conn.close()

    return render_template(
        'transport_dashboard.html',vehicles=vehicles,
        name=session.get('name', 'Transportador'),
        vehiculos=vehiculos
    )














@app.route('/tus_vehiculos', methods=['GET'])
def tus_vehiculos():

    if 'user_id' not in session or session['role'] != 'transportador':
        return redirect(url_for('index'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()


    user_id = session['user_id']  
    
    cursor.execute("""
        SELECT v.id, v.modelo, v.placa, v.ubicacion, v.estado, v.cliente_telefono, 
            v.cliente_nombre, v.numero_vuelo, v.numero_reserva, 
            v.fecha_entrega, v.hora_entrega,v.hora_recogida
        FROM vehiculos v
        WHERE v.estado IN ('en recogida', 'en entrega')
    """)

    vehicles = cursor.fetchall() 

    cursor.close()
    conn.close()

   
    print(vehicles)

    return render_template('tus_Vehiculos.html', vehicles=vehicles, name=session.get('name', 'Transportador'))





@app.route('/finalizar_proceso/<numero_reserva>', methods=['POST'])
def finalizar_proceso(numero_reserva):

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Obtener estado actual del vehículo por numero_reserva
    cursor.execute("""
        SELECT estado
        FROM vehiculos
        WHERE numero_reserva = %s
    """, (numero_reserva,))
    
    estado_actual = cursor.fetchone()

    if not estado_actual:
        cursor.close()
        conn.close()
        flash('Reserva no encontrada.', 'error')
        return redirect(url_for('tus_vehiculos'))

    estado_actual = estado_actual[0].lower()

    # Determinar nuevo estado y usuario asociado
    if estado_actual == 'en recogida':
        nuevo_estado = 'recogido'
        columna_usuario = 'usuario_recogida'
    elif estado_actual == 'en entrega':
        nuevo_estado = 'entregado'
        columna_usuario = 'usuario_entrega'
    else:
        cursor.close()
        conn.close()
        flash('El estado actual no permite finalizar el proceso.', 'error')
        return redirect(url_for('tus_vehiculos'))

    user_id = session.get('user_id')

    comentario = request.form.get('comentario')
    nueva_ubicacion = request.form.get('nueva_ubicacion')
    fotos = request.files.getlist('fotos')

    upload_folder = 'uploads/peritajes'
    os.makedirs(upload_folder, exist_ok=True)

    fotos_guardadas = []

    if fotos:
        for foto in fotos:
            if foto and allowed_file(foto.filename): 
                filename = secure_filename(foto.filename)
                foto_path = os.path.join(upload_folder, filename)
                foto.save(foto_path)
                fotos_guardadas.append(filename)

    if comentario:
        cursor.execute("""
            UPDATE vehiculos
            SET comentarios = %s
            WHERE numero_reserva = %s
        """, (comentario, numero_reserva))

    if nueva_ubicacion:
        cursor.execute("""
            UPDATE vehiculos
            SET ubicacion = %s
            WHERE numero_reserva = %s
        """, (nueva_ubicacion, numero_reserva))

    for filename in fotos_guardadas:
        cursor.execute("""
            INSERT INTO peritaje (numero_reserva, fotos, fecha_peritaje)
            VALUES (%s, %s, NOW())
        """, (numero_reserva, filename))

    cursor.execute(f"""
        UPDATE vehiculos
        SET estado = %s, {columna_usuario} = %s
        WHERE numero_reserva = %s
    """, (nuevo_estado, user_id, numero_reserva))

    conn.commit()

    cursor.close()
    conn.close()

    flash(f'Proceso finalizado. La reserva {numero_reserva} ha sido actualizada a "{nuevo_estado}".', 'success')
    return redirect(url_for('tus_vehiculos'))




def allowed_file(filename):
    """
    Verificar si el archivo tiene una extensión permitida.
    """
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions























@app.route('/peritajes', methods=['GET'])
def peritajes():
    

    if 'user_id' not in session or session['role'] != 'administrativo':
        return redirect(url_for('index'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    user_id = session['user_id']  

    # Ahora seleccionamos peritajes usando numero_reserva
    cursor.execute("""
        SELECT v.numero_reserva, v.modelo, v.estado, v.ubicacion, p.fotos, v.placa
        FROM vehiculos v
        LEFT JOIN peritaje p ON v.numero_reserva = p.numero_reserva
        WHERE p.fotos IS NOT NULL
        GROUP BY v.numero_reserva
    """)
    vehiculos_peritados = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('peritaje.html', 
                           name=session.get('name', 'Administrativo'),
                           vehiculos_peritados=vehiculos_peritados)


@app.route('/detalles_peritaje/<numero_reserva>', methods=['GET'])
def detalles_peritaje(numero_reserva):

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Obtener fotos del peritaje por numero_reserva
    cursor.execute("SELECT numero_reserva, fotos, fecha_peritaje FROM peritaje WHERE numero_reserva = %s", (numero_reserva,))
    vehiculos = cursor.fetchall()

    # Obtener detalles del vehículo por numero_reserva
    cursor.execute("""
        SELECT id, modelo, placa, fecha_recogida, hora_recogida, fecha_entrega, hora_entrega, cliente_nombre, cliente_telefono, cliente_correo, comentarios, 
               descripcion, numero_reserva, ubicacion, estado 
        FROM vehiculos WHERE numero_reserva = %s
    """, (numero_reserva,))
    
    detalles_vehiculo = cursor.fetchall()

    cursor.close()
    conn.close()

    print("Fotos en la base de datos:", vehiculos)

    if vehiculos and detalles_vehiculo:
        fotos = [vehiculo[1].split(',') for vehiculo in vehiculos if vehiculo[1]]
        fotos = [foto.strip() for sublist in fotos for foto in sublist]

        detalles = detalles_vehiculo[0]

        return render_template('detalles_peritaje.html',
                               name=session.get('name', 'Transportador'),
                               vehiculo=vehiculos, 
                               fotos=fotos, 
                               detalles=detalles)
    else:
        return f"No se encontró el peritaje para la reserva {numero_reserva}"








app.config['UPLOAD_FOLDER'] = 'uploads/peritajes'

@app.route('/uploads/peritajes/<filename>')
def uploaded_file(filename):

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)































from datetime import timedelta, datetime


@app.route('/editar_vehiculo/<int:vehicle_id>', methods=['GET', 'POST'])
def editar_vehiculo(vehicle_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))  

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT v.id, v.modelo, v.fecha_recogida, v.hora_recogida, v.fecha_entrega, v.hora_entrega, 
                   v.cliente_nombre, v.cliente_telefono, v.descripcion, v.placa, 
                   v.ubicacion,v.numero_vuelo, v.estado, v.numero_reserva,
                   ue.nombre AS usuario_entrega_nombre, ur.nombre AS usuario_recogida_nombre
            FROM vehiculos v
            LEFT JOIN usuarios ue ON v.usuario_entrega = ue.id
            LEFT JOIN usuarios ur ON v.usuario_recogida = ur.id
            WHERE v.id = %s
        """, (vehicle_id,))
        vehicle = cursor.fetchone()

        if not vehicle:
            cursor.close()
            conn.close()
            return redirect(url_for('ver_vehiculos'))  


        if isinstance(vehicle['hora_recogida'], timedelta):
            vehicle['hora_recogida'] = (datetime.min + vehicle['hora_recogida']).strftime('%H:%M')
        if isinstance(vehicle['hora_entrega'], timedelta):
            vehicle['hora_entrega'] = (datetime.min + vehicle['hora_entrega']).strftime('%H:%M')



        if request.method == 'POST':
            action = request.form.get('action', 'update')
            
            if action == 'delete':
                cursor.execute("DELETE FROM vehiculos WHERE id = %s", (vehicle_id,))
                conn.commit()
                return redirect(url_for('ver_vehiculos')) 

            modelo = request.form['modelo']
            placa = request.form['placa']
            fecha_recogida = request.form['fecha_recogida']
            hora_recogida = request.form['hora_recogida']
            fecha_entrega = request.form['fecha_entrega']
            hora_entrega = request.form['hora_entrega']
            cliente_nombre = request.form['cliente_nombre']
            cliente_telefono = request.form['cliente_telefono']
            numero_reserva = request.form['numero_reserva']
            descripcion = request.form['descripcion']
            ubicacion = request.form['ubicacion']
            numero_vuelo=request.form['numero_vuelo']
            estado = request.form['estado']

            cursor.execute("""
                UPDATE vehiculos SET 
                    modelo = %s, 
                    placa = %s,
                    
                    fecha_recogida = %s, 
                    hora_recogida = %s, 
                    fecha_entrega = %s, 
                    hora_entrega = %s, 
                    cliente_nombre = %s, 
                    cliente_telefono = %s, 
                    numero_reserva = %s,
                    descripcion = %s, 
                    
                    ubicacion = %s, 
                    numero_vuelo = %s,       
                    estado = %s
                WHERE id = %s
            """, (modelo, placa, fecha_recogida, hora_recogida, fecha_entrega, hora_entrega, cliente_nombre, cliente_telefono, numero_reserva,
                   descripcion, ubicacion, numero_vuelo, estado, vehicle_id))
            conn.commit()

            return redirect(url_for('ver_vehiculos'))

    finally:
        cursor.close()
        conn.close()

    return render_template('editar_vehiculo.html', vehicle=vehicle, name=session.get('name', 'Administrador'))





















def obtener_ganancias_y_vehiculos(filtro, valor):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Verificamos si es mes o año
    if filtro == 'mes':
        cursor.execute("""
            SELECT DATE_FORMAT(fecha_recogida, '%Y-%m') AS periodo, SUM(precio) AS total_ganancias
            FROM vehiculos
            WHERE fecha_recogida IS NOT NULL AND DATE_FORMAT(fecha_recogida, '%Y-%m') = %s
            GROUP BY periodo
            ORDER BY periodo DESC;
        """, (valor,))
    elif filtro == 'anio':
        cursor.execute("""
            SELECT DATE_FORMAT(fecha_recogida, '%Y') AS periodo, SUM(precio) AS total_ganancias
            FROM vehiculos
            WHERE fecha_recogida IS NOT NULL AND DATE_FORMAT(fecha_recogida, '%Y') = %s
            GROUP BY periodo
            ORDER BY periodo DESC;
        """, (str(valor),))

    ganancias = cursor.fetchall()

    # Consulta para obtener los vehículos registrados en el mes o año seleccionado
    if filtro == 'mes':
        cursor.execute("""
            SELECT modelo, placa, precio 
            FROM vehiculos 
            WHERE fecha_recogida IS NOT NULL AND DATE_FORMAT(fecha_recogida, '%Y-%m') = %s
            ORDER BY precio DESC;
        """, (valor,))
    elif filtro == 'anio':
        cursor.execute("""
            SELECT modelo, placa, precio 
            FROM vehiculos 
            WHERE fecha_recogida IS NOT NULL AND DATE_FORMAT(fecha_recogida, '%Y') = %s
            ORDER BY precio DESC;
        """, (str(valor),))

    vehiculos = cursor.fetchall()
    
    conn.close()
    return ganancias, vehiculos

@app.route('/Ganancias', methods=['GET', 'POST'])
def Ganancias():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    filtro = request.form.get('filtro', 'mes')  
    valor = request.form.get('valor')


    if not valor:
        valor = datetime.now().strftime('%Y-%m') if filtro == 'mes' else datetime.now().strftime('%Y')


    try:
        if filtro == 'anio':
            valor = int(valor)  
            if valor < 2025:
                valor = 2025
            valor = str(valor)  
        elif filtro == 'mes':
            if int(valor[:4]) < 2025:
                valor = "2025-01"
    except ValueError:
        valor = "2025-01" if filtro == 'mes' else "2025"

    ganancias, vehiculos = obtener_ganancias_y_vehiculos(filtro, valor)
    
    return render_template('ganancias.html', 
                           name=session.get('name', 'Administrador'),
                           ganancias=ganancias, 
                           vehiculos=vehiculos,
                           filtro=filtro,
                           valor=valor)



@app.route('/create_vehicle2', methods=['GET', 'POST'])
def create_vehicle2():
    if 'user_id' not in session or session['role'] != 'administrativo':
        return redirect(url_for('index'))  

    if request.method == 'POST':
        file = request.files['csv_file']
        if file:
            stream = file.stream.read().decode("utf-8").splitlines()
            reader = csv.reader(stream)
            next(reader)  

            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            for row in reader:
                numero_reserva = row [0]
                modelo = row[4]
                placa = row[5]
                fecha_recogida = row[12].split(' ')[0] if ' ' in row[13] else row[13]
                hora_recogida = row[12].split(' ')[1] if ' ' in row[13] else "00:00:00"
                estado = "Recogida"
                cliente_nombre = row[1]
                cliente_telefono = row[3]
                fecha_entrega = row[13].split(' ')[0] if ' ' in row[14] else row[14]
                hora_entrega = row[13].split(' ')[1] if ' ' in row[14] else "00:00:00"
                precio = row[15]

                cursor.execute("""
                    INSERT INTO vehiculos (numero_reserva, modelo, placa, fecha_recogida, hora_recogida,  estado,  cliente_nombre, cliente_telefono,  fecha_entrega, hora_entrega, precio)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (numero_reserva, modelo, placa, fecha_recogida, hora_recogida,  estado,  cliente_nombre, cliente_telefono,  fecha_entrega, hora_entrega, precio))

            conn.commit()
            cursor.close()
            conn.close()

        return redirect(url_for('ver_vehiculos'))

    return render_template('create_vehicle2.html', name=session.get('name', 'Administrador'))













@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'  # Asegúrate de tener una clave secreta para la sesión
    app.run(host="0.0.0.0", port="8000", debug=False)