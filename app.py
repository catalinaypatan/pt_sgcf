import flask
import smtplib
import dotenv
import os
import datetime
import mysql.connector
import secrets
#test
dotenv.load_dotenv()

app =  flask.Flask('TrabajoListas')
app.secret_key = os.getenv("clave_secreta_flask")

app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=15)


#----------------------------------------------------------------
def enviar_correo(p_para, p_asunto, p_mensaje):
    email = os.getenv("email_envio_correo")
    contrasenha = os.getenv("contrasena_envio_correo")
    smtpserver = smtplib.SMTP_SSL(os.getenv("host_envio_correo"), int(os.getenv("puerto_envio_correo")))
    smtpserver.ehlo()
    smtpserver.login(email, contrasenha)

    desde = email
    para = p_para
    contenido = f"Subject: {p_asunto}\n\n{p_mensaje}"
    smtpserver.sendmail(desde, para, contenido)
    smtpserver.close()

#----------------------------------------------------------------
def consultar_base_datos(query):
    resultados = []

    with mysql.connector.connect(
            host=os.getenv("host_bd"),
            user=os.getenv("usuario_bd"),
            password=os.getenv("contrasena_bd"),
            database=os.getenv("nombre_bd")
    ) as conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(query)
        filas_obtenidas_con_query = cursor.fetchall()

        for fila in filas_obtenidas_con_query:
            fila_como_diccionario = dict(fila)
            resultados.append(fila_como_diccionario)

        cursor.close()

    return resultados


#----------------------------------------------------------------
def ejecutar_base_datos(query):
    with mysql.connector.connect(
            host=os.getenv("host_bd"),
            user=os.getenv("usuario_bd"),
            password=os.getenv("contrasena_bd"),
            database=os.getenv("nombre_bd")
    ) as conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(query)

        conexion.commit()
        cursor.close()


#----------------------------------------------------------------
@app.route("/")
def redireccionar_primera_pagina():
    return flask.redirect("/inicio_sesion")


#----------------------------------------------------------------
@app.route("/inicio_sesion")
def enviar_a_html_inicio_sesion():
    flask.session.pop("usuario_logeado", None)
    return flask.render_template("inicio.html")


#----------------------------------------------------------------
@app.route("/generar_codigo_verificacion", methods=["post"])
def generar_codigo_verificacion():

    campos_formulario = flask.request.form
    email = campos_formulario.get("email")

    usuarios_en_bd = consultar_base_datos(f"select * from usuarios where correo ='{email}'")

    if len(usuarios_en_bd) == 0:
        flask.flash("⚠️ El correo entregado no cuenta con acceso al sistema")
        return flask.redirect('/inicio_sesion')

    codigo_verificacion = secrets.token_urlsafe(5)

    flask.session["datos_verificacion"] = {
        "codigo_verificacion" : codigo_verificacion,
        "email" : email
    }

    #Se envia mensaje sin tildes para evitar problemas con el envio correo
    enviar_correo(email, "SGCF - Codigo de verificacion", f"El codigo de verificacion es el siguiente: {codigo_verificacion}")

    return flask.redirect("/codigo_verificacion")


#----------------------------------------------------------------
@app.route("/codigo_verificacion")
def enviar_a_html_codigo_verificacion():
    return flask.render_template("codigo_verificacion.html")


#----------------------------------------------------------------
@app.route("/validar_codigo_verificacion", methods=["post"])
def validar_codigo_verificacion():

    campos_formulario = flask.request.form
    codigo = campos_formulario.get("code")

    datos_verificacion = flask.session.get("datos_verificacion")
    if datos_verificacion == None:
        flask.flash("⚠️ El código de verificación ha vencido")
        return flask.redirect("/inicio_sesion")


    codigo_verificacion = datos_verificacion.get("codigo_verificacion")

    if codigo_verificacion != codigo:
        flask.flash("⚠️ El código de verificación ingresado es incorrecto")
        return flask.redirect("/codigo_verificacion")


    email_verificacion = datos_verificacion.get("email")

    usuarios_en_bd = consultar_base_datos(f"select * from usuarios where correo = '{email_verificacion}'")

    usuario = usuarios_en_bd[0]

    flask.session["usuario_logeado"] = usuario

    return flask.redirect("/menu")


#----------------------------------------------------------------
@app.route("/menu")
def enviar_a_html_menu():

    usuario_logeado = flask.session.get("usuario_logeado")
    if usuario_logeado == None:
        return flask.redirect("/inicio_sesion")

    return flask.render_template("menu.html")


# ----------------------------------------------------------------
@app.route("/actualiza_tus_contactos/<nombre_lista>")
def enviar_a_html_actualiza_tus_contactos(nombre_lista):

    usuario_logeado = flask.session.get("usuario_logeado")
    if usuario_logeado == None:
        return flask.redirect("/inicio_sesion")

    if nombre_lista not in ["Docu", "Copy of BL", "Arrival Notice"]:
        return flask.redirect("/menu")

    if nombre_lista == "Docu":
        titulo = "Documentos"
    elif nombre_lista == "Copy of BL":
        titulo = "Finanzas"
    elif nombre_lista == "Arrival Notice":
        titulo = "Aviso de llegada"
    else:
        titulo = ""

    correos_bd = consultar_base_datos(f"""
        select * 
        from correos_actuales 
        where 
            match_code_empresa = '{usuario_logeado.get("match_code_empresa")}' 
            and nombre_lista = '{nombre_lista}' 
    """)

    solicitudes_bd = consultar_base_datos(f"""
        select * 
        from solicitudes 
        where 
            match_code_empresa = '{usuario_logeado.get("match_code_empresa")}' 
            and nombre_lista = '{nombre_lista}' 
            and estado_solicitud = 'pendiente'
    """)

    return flask.render_template("actualiza_tus_contactos.html", nombre_lista=nombre_lista, titulo= titulo, correos_bd = correos_bd, solicitudes_bd= solicitudes_bd)


#----------------------------------------------------------------
@app.route('/agregar_contacto', methods=['post'])
def agregar_contacto():

    usuario_logeado = flask.session.get("usuario_logeado")

    if usuario_logeado == None:
        return flask.redirect("/inicio_sesion")

    campos_formulario = flask.request.form
    correo_nuevo = campos_formulario.get('email_nuevo')
    nombre_lista = campos_formulario.get('nombre_lista')

    if nombre_lista not in ["Docu", "Copy of BL", "Arrival Notice"]:
        flask.flash('⚠️ La lista asociada a la solicitudd no es una lista valida')
        return flask.redirect(flask.request.referrer)

    match_code = usuario_logeado.get('match_code_empresa')
    correo_solicitante = usuario_logeado.get('correo')

    correos_bd = consultar_base_datos(f"""
        select * 
        from correos_actuales 
        where 
            correo = '{correo_nuevo}' 
            and match_code_empresa = '{match_code}' 
            and nombre_lista = '{nombre_lista}'
    """)

    if len(correos_bd) > 0:
        flask.flash(f'⚠️ El contacto {correo_nuevo} que solicito agregar ya existe')
        return flask.redirect(flask.request.referrer)

    solicitudes_bd = consultar_base_datos(f"""
        select * 
        from solicitudes 
        where 
            correo = '{correo_nuevo}' 
            and match_code_empresa = '{match_code}' 
            and nombre_lista = '{nombre_lista}'  
            and tipo_solicitud = 'agregar' 
            and estado_solicitud = 'pendiente'
    """)

    if len(solicitudes_bd) > 0:
        flask.flash(f'⚠️ Ya existe una solicitud pendiente para la inclusión del contacto {correo_nuevo}')
        return flask.redirect(flask.request.referrer)

    ejecutar_base_datos(f"""
        insert into solicitudes (
            correo_solicitante, 
            tipo_solicitud, 
            correo, 
            match_code_empresa, 
            nombre_lista, 
            estado_solicitud
        ) values (
            '{correo_solicitante}', 
            'agregar', 
            '{correo_nuevo}', 
            '{match_code}', 
            '{nombre_lista}', 
            'pendiente'
        )
    """)

    return flask.redirect(flask.request.referrer)


#----------------------------------------------------------------
@app.route('/eliminar_contacto/<id_correo>', methods=['post'])
def eliminar_contacto(id_correo):

    usuario_logeado = flask.session.get("usuario_logeado")

    if usuario_logeado == None:
        return flask.redirect("/inicio_sesion")

    correos_actuales_bd = consultar_base_datos(f"""
        select * 
        from correos_actuales 
        where 
            id = {id_correo} 
            and match_code_empresa = '{usuario_logeado.get('match_code_empresa')}'
    """)

    if len(correos_actuales_bd) == 0:
        flask.flash(f'🛑 No se encontro un correo con un id coincidente que este asociado a la empresa del usuario')
        return flask.redirect(flask.request.referrer)

    correo_bd = correos_actuales_bd[0]

    #datos de la solicitud
    correo_a_borrar = correo_bd.get('correo')
    nombre_lista = correo_bd.get('nombre_lista')
    match_code = usuario_logeado.get('match_code_empresa')
    correo_solicitante = usuario_logeado.get('correo')


    solicitudes_bd = consultar_base_datos(f"""
        select * 
        from solicitudes 
        where 
            correo = '{correo_a_borrar}' 
            and match_code_empresa = '{match_code}' 
            and nombre_lista = '{nombre_lista}' 
            and tipo_solicitud = 'eliminar' 
            and estado_solicitud = 'pendiente'
    """)

    if len(solicitudes_bd) > 0:
        flask.flash(f'⚠️ Ya existe una solicitud pendiente para la eliminación del contacto {correo_a_borrar}')
        return flask.redirect(flask.request.referrer)

    ejecutar_base_datos(f"""
        insert into solicitudes (
            correo_solicitante, 
            tipo_solicitud, 
            correo, 
            match_code_empresa, 
            nombre_lista, 
            estado_solicitud
        ) values (
            '{correo_solicitante}', 
            'eliminar', 
            '{correo_a_borrar}', 
            '{match_code}', 
            '{nombre_lista}', 
            'pendiente'
        )
    """)

    return flask.redirect(flask.request.referrer)


#----------------------------------------------------------------
@app.route('/eliminar_solicitud/<id_solicitud>', methods=['post'])
def eliminar_solicitud(id_solicitud):

    usuario_logeado = flask.session.get("usuario_logeado")

    if usuario_logeado == None:
        return flask.redirect("/inicio_sesion")

    match_code = usuario_logeado.get('match_code_empresa')
    correo_anulador = usuario_logeado.get('correo')

    ejecutar_base_datos(f"""
        update solicitudes 
        set 
            estado_solicitud = 'anulada', 
            anulada_por = '{correo_anulador}' 
        where 
            id = {id_solicitud} 
            and match_code_empresa = '{match_code}'
    """)

    return flask.redirect(flask.request.referrer)

#----------------------------------------------------------------
app.run(debug=True)