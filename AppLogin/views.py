from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth import logout as django_logout 
from TR.models import Usuario,Pago,Estudiante,Operador, AccesoMatriculas
from .decorators import rol_required,usuario_autenticado 
from django.contrib import messages
from datetime import date, datetime
from django.utils.timezone import now
from datetime import timedelta


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('T_NombreUsuario', '').strip()
        password = request.POST.get('T_Contrasenia', '').strip()
        # Obtener intentos fallidos de la sesión
        intentos_fallidos = request.session.get('intentos_fallidos', 3)
        tiempo_bloqueo_str = request.session.get('tiempo_bloqueo')

        # Verificar si el usuario está bloqueado
        tiempo_bloqueo = None
        if tiempo_bloqueo_str:
            try:
                tiempo_bloqueo = datetime.fromisoformat(tiempo_bloqueo_str)
            except ValueError:
                tiempo_bloqueo = None

        # Verificar si el usuario está bloqueado
        if tiempo_bloqueo and now() < tiempo_bloqueo:
            messages.error(request, 'Demasiados intentos fallidos. Inténtalo más tarde.')
            return redirect('login')
        
        if not username or not password:
            messages.error(request, 'Por favor, completa todos los campos.')
            return redirect('login')

        try:
            usuario = Usuario.objects.get(T_NombreUsuario=username)
            if check_password(password, usuario.T_Contrasenia):
                request.session['intentos_fallidos'] = 0
                request.session['tiempo_bloqueo'] = None
                # Configurar la sesión con el ID y el nombre del rol
                request.session['I_UsuarioID'] = usuario.I_UsuarioID
                request.session['T_NombreUsuario'] = usuario.T_NombreUsuario
                request.session['T_Nombre'] = usuario.T_Nombre
                request.session['I_RolID'] = usuario.I_RolID.I_RolID  # Guardamos el ID del rol aquí
                rol = usuario.I_RolID.I_RolID  # Aquí usamos el nombre del rol
                
                # Redirigir según el nombre del rol
                if rol == 1:
                    try:
                        estudiante_codigo = username.split('@')[0]
                        # Ahora realizamos la consulta con el código extraído

                        if not Pago.objects.filter(N_CodEstudianteID=estudiante_codigo).exists():
                            logout_view(request)
                            messages.error(request, 'No se ha registrado ningún pago para este estudiante. No puedes acceder al sistema.')
                            return redirect('login')  # Redirigir al login

                        acceso_valido, mensaje = validar_acceso_estudiante(estudiante_codigo)
                        if acceso_valido:
                            return redirect('terminos_condiciones')
                        else:
                            messages.error(request, mensaje)
                            
                    except Estudiante.DoesNotExist:
                        print("no existe")
                        return redirect('login')
                elif rol == 2:
                    try:
                        operador_codigo = username.split('@')[0]
                        # Ahora realizamos la consulta con el código extraído
                        Operador.objects.get(N_CodOperadorID=operador_codigo)
                        return redirect('operador_horarios')
                    except Operador.DoesNotExist:
                        messages.error(request, 'El operador no existe.')
                        return redirect('login')
                elif rol == 3:
                    return redirect('ocrac_historial')
                elif rol ==4:
                    return redirect('eliminar_matricula')
                else:
                    messages.error(request, 'Rol desconocido.')
                    return redirect('login')
            else:
                intentos_fallidos -= 1
                messages.error(request, f'Usuario o contraseña incorrectos. Le queda {intentos_fallidos} intento restante.' if intentos_fallidos == 1 else f'Usuario o contraseña incorrectos. Le quedan {intentos_fallidos} intentos restantes.')
        except Usuario.DoesNotExist:
            messages.error(request, f'El usuario no Existe. Le queda {intentos_fallidos} intento restante.' if intentos_fallidos == 1 else f'El usuario no Existe. Le quedan {intentos_fallidos} intentos restantes.')
            intentos_fallidos -= 1
        
        request.session['intentos_fallidos'] = intentos_fallidos

        # Bloquear después de 3 intentos fallidos
        if intentos_fallidos <= 0:
            bloqueo_time = now() + timedelta(minutes=5)
            request.session['tiempo_bloqueo'] = bloqueo_time.isoformat()  # Guardar como string
            messages.error(request, 'Has excedido el número de intentos. Intenta de nuevo en 5 minutos.')
            return redirect('login')
    response = render(request, 'Login/Login.html')
    response['Cache-Control'] = 'no-store'  # Evitar caché
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


def logout_view(request):
    # Elimina las variables de sesión personalizadas
    if 'I_UsuarioID' in request.session:
        del request.session['I_UsuarioID']
    if 'T_NombreUsuario' in request.session:
        del request.session['T_NombreUsuario']
    if 'I_RolID' in request.session:
        del request.session['I_RolID']

    # Utiliza el logout de Django para limpiar la sesión
    django_logout(request)

    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('login')  # Redirige al login después de cerrar sesión


@rol_required("Estudiante")
@usuario_autenticado
def estudiante_pago(request):
    # Obtener el código del estudiante desde la sesión
    usuario_codigo  = request.session.get("T_NombreUsuario")  # Ajustar según tu lógica de sesión
    estudiante_codigo = usuario_codigo .split('@')[0]
    estudiante = get_object_or_404(Estudiante, N_CodEstudianteID=estudiante_codigo)

    # Obtener los datos generales del estudiante usando la lógica de datos_estudiante
    datos_context = datos_estudiante(request)

    # Obtener el último pago realizado por el estudiante
    ultimo_pago = Pago.objects.filter(N_CodEstudianteID=estudiante).order_by('-D_FechaPago').first()

    # Agregar la información del último pago al contexto
    context = {
        **datos_context,  # Añadimos todos los datos del estudiante obtenidos en datos_estudiante
        "entidad_pago": ultimo_pago.I_EntidadID.T_NombreEntidad if ultimo_pago else None,
        "codigo_liquidacion": ultimo_pago.T_CodLiquidacion if ultimo_pago else None,
        "fecha_pago": ultimo_pago.D_FechaPago if ultimo_pago else None,
    }
    return render(request, 'Estudiante/Estudiante_Pago.html', context)


def datos_estudiante(request):
    # Obtener el código del estudiante desde la sesión
    usuario_codigo  = request.session.get("T_NombreUsuario")  # Ajustar según tu lógica de sesión
    estudiante_codigo = usuario_codigo .split('@')[0]
    estudiante = get_object_or_404(Estudiante, N_CodEstudianteID=estudiante_codigo)
    print("Datos de inicio de sesion: ",estudiante_codigo)
    # Datos del plan curricular y la carrera
    plan_curricular = estudiante.I_PlanID
    especialidad = plan_curricular.I_EspecialidadID
    escuela = especialidad.I_EscuelaID
    facultad = escuela.I_FacultadID

    # Contexto con la información solicitada
    context = {
        "codigo_estudiante": estudiante.N_CodEstudianteID,
        "nombre_estudiante": f"{estudiante.T_ApelPaterno} {estudiante.T_ApelMaterno} {estudiante.T_Nombre}",
        "facultad": facultad.T_NombreFacultad,  # Nombre de la facultad
        "escuela": escuela.T_NombreEscuela,  # Nombre de la escuela
        "especialidad": especialidad.T_NombreEspecialidad,  # Nombre de la especialidad
        "anio_ingreso": estudiante.I_AnioIngreso,
        "plan_estudio": plan_curricular.I_AnioPlan,  # Año del plan curricular
        "ultimo_semestre": estudiante.I_UltiSemestreCursado,
        "nivel": estudiante.I_Nivel + 1,
    }
    return context


# Vista protegida para OCRAC (solo accesible por usuarios con rol 8)
@rol_required("OCRAC")
@usuario_autenticado
def ocrac_historial(request):
    return render(request, 'OCRAC/OCRAC_Historial.html')


def validar_acceso_estudiante(estudiante_codigo):
    try:
        # Obtener el estudiante y el acceso de matrícula
        estudiante = Estudiante.objects.get(N_CodEstudianteID=estudiante_codigo)

        # Obtener el acceso de matrícula para validar las fechas y la categoría
        acceso_quinto = AccesoMatriculas.objects.first()  # Obtener el primer acceso de matrícula (esto se puede modificar según tu lógica)
        acceso_regular = AccesoMatriculas.objects.all()[1]
        acceso_rezagado = AccesoMatriculas.objects.all()[2]
        
        # Validación para acceso rezagado
        fecha_inicio_rezagado = datetime.combine(acceso_rezagado.D_DiaApertura, acceso_rezagado.D_HoraApertura)
        fecha_fin_rezagado = datetime.combine(acceso_rezagado.D_DiaCierre, acceso_rezagado.D_HoraCierre)
        if fecha_inicio_rezagado <= datetime.now() <= fecha_fin_rezagado:
            return True, ""

        # Validación para acceso quinto superior
        if estudiante.B_QuintoSuperior:
            fecha_inicio_quinto = datetime.combine(acceso_quinto.D_DiaApertura, acceso_quinto.D_HoraApertura)
            fecha_fin_quinto = datetime.combine(acceso_quinto.D_DiaCierre, acceso_quinto.D_HoraCierre)
            if fecha_inicio_quinto <= datetime.now() <= fecha_fin_quinto:
                return True, ""
            else:
                return False, f"Fecha fuera del rango: {date.today()}"
        
        # Validación para acceso regular
        fecha_inicio_regular = datetime.combine(acceso_regular.D_DiaApertura, acceso_regular.D_HoraApertura)
        fecha_fin_regular = datetime.combine(acceso_regular.D_DiaCierre, acceso_regular.D_HoraCierre)
        if fecha_inicio_regular <= datetime.now() <= fecha_fin_regular:
            return True, ""
        else:
            return False, f"Fecha fuera del rango: {date.today()}"
    
    except Estudiante.DoesNotExist:
        return False, f"Estudiante con código {estudiante_codigo} no encontrado."
    except AccesoMatriculas.DoesNotExist:
        return False, "No se encontró un acceso de matrícula."
    
@rol_required("Estudiante")
@usuario_autenticado
def terminos_condiciones (request): 
    datos = datos_estudiante(request)

    if request.method == 'POST':
        return redirect('estudiante_pago')

    context= {
        **datos
    }
    return render(request, 'Estudiante/Terminos_Condiciones.html',context)