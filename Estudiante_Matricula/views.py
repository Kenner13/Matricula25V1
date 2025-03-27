from django.shortcuts import render, redirect,get_object_or_404
from AppLogin.views import datos_estudiante
from django.utils import timezone
from TI.models import Matricula
from TR.models import AccesoMatriculas, HistorialAcademicos, AsignaturaPreRequisitos, Asignatura, Pago, Programacion,Estudiante   
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.templatetags.static import static
import json
import io
import os
from django.conf import settings
from datetime import datetime
from datetime import timedelta
from xhtml2pdf import pisa
from django.http import JsonResponse
from AppLogin.decorators import rol_required,usuario_autenticado
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Create your views here.
def obtener_estudiante_desde_sesion(request):
    usuario_codigo = request.session.get("T_NombreUsuario")
    estudiante_codigo = usuario_codigo.split('@')[0]  # Ajuste según la lógica de sesión
    return get_object_or_404(Estudiante, N_CodEstudianteID=estudiante_codigo)

def obtener_asignaturas_dependientes(aprobadas):
    asignaturas_dependientes = set()
    for asignatura in aprobadas:
        # Encontramos asignaturas que tienen esta como prerrequisito
        prerequisitos = AsignaturaPreRequisitos.objects.filter(
            I_PreRequisitoID=asignatura
        ).values_list('I_AsignaturaID', flat=True)
        
        # Agregamos las asignaturas encontradas a la lista de dependientes
        asignaturas_dependientes.update(prerequisitos)
        
        # Llamada recursiva para seguir buscando dependientes en cadena
        asignaturas_dependientes.update(obtener_asignaturas_dependientes(prerequisitos))
    
    return asignaturas_dependientes

def agrupar_programaciones(estudiante, asignaturas_filtradas):
    programaciones = Programacion.objects.filter(
        I_AsignaturaID__I_PlanID=estudiante.I_PlanID,
        I_AsignaturaID__in=asignaturas_filtradas,
        B_Habilitado=1
    )

    programaciones_agrupadas = {}

    for programacion in programaciones:
        asignatura_id = programacion.I_AsignaturaID.I_AsignaturaID
        vez_llevado = HistorialAcademicos.objects.filter(
            N_CodEstudianteID=estudiante, 
            I_AsignaturaID=asignatura_id
        ).values_list('I_VezLlevadoAsignatura', flat=True)
        
        vez_llevado = vez_llevado.first() + 1 if vez_llevado else 1

        key = (programacion.I_AsignaturaID, programacion.C_Seccion)
        if key not in programaciones_agrupadas:
            programaciones_agrupadas[key] = {
                'ID': [],
                'periodo': programacion.C_Periodo,
                'ciclo': programacion.I_AsignaturaID.T_Ciclo,
                'codigo_asignatura': programacion.I_AsignaturaID.I_CodAsignatura,
                'asignatura': programacion.I_AsignaturaID.T_NombreAsignatura,
                'turno': programacion.C_Turno,
                'creditos': programacion.I_AsignaturaID.I_Creditos,
                'seccion': programacion.C_Seccion,
                'dias': [],
                'horas': [],
                'docentes': f"{programacion.N_CodDocenteID.T_ApelPaterno} {programacion.N_CodDocenteID.T_ApelMaterno} {programacion.N_CodDocenteID.T_Nombre}",
                'aula': programacion.T_Aula,
                'cupos': programacion.I_Cupos,
                'vez_llevado': vez_llevado,
                'condicion': programacion.I_AsignaturaID.I_CondicionAsignaturaID.T_NombreCondicion,
            }

        programaciones_agrupadas[key]['ID'].append(programacion.I_ProgramacionID)

        horas_inicio = [programacion.D_HoraInicio1, programacion.D_HoraInicio2, programacion.D_HoraInicio3]
        horas_fin = [programacion.D_HoraFin1, programacion.D_HoraFin2, programacion.D_HoraFin3]

        for inicio, fin in zip(horas_inicio, horas_fin):
            if inicio:  # Solo agregar si hay una hora de inicio válida
                programaciones_agrupadas[key]['horas'].append(f"{inicio} - {fin}")

        for dia, dia_id in [(programacion.I_DiaID1, programacion.I_DiaID1), 
                            (programacion.I_DiaID2, programacion.I_DiaID2), 
                            (programacion.I_DiaID3, programacion.I_DiaID3)]:
            if dia and dia_id.I_DiaID != 0:
                programaciones_agrupadas[key]['dias'].append(dia.T_NombreDia)

    programaciones_agrupadas_list = [
        {
            'ID': list(map(int, value['ID'])),
            'periodo': value['periodo'],
            'ciclo': value['ciclo'],
            'codigo_asignatura': value['codigo_asignatura'],
            'asignatura': value['asignatura'],
            'condicion': value['condicion'],
            'turno': value['turno'],
            'creditos': value['creditos'],
            'seccion': value['seccion'],
            'dias': ' | '.join(value['dias']),
            'horas': ' | '.join(value['horas']),
            'docentes': value['docentes'],
            'aula': value['aula'],
            'cupos': value['cupos'],
            'vez_llevado': value['vez_llevado'],
        }
        for value in programaciones_agrupadas.values()
    ]

    programaciones_agrupadas_list.sort(key=lambda x: (x['periodo'], x['condicion'][::-1], x['codigo_asignatura'], x['seccion'], x['ciclo'], -x['vez_llevado']))

    return programaciones_agrupadas_list


def obtener_programaciones_estudiante(estudiante):
        # Obtener el ciclo actual del estudiante (último semestre cursado)
        ultimo_semestre_estudiante = estudiante.I_UltiSemestreCursado
        print(ultimo_semestre_estudiante)
        # Obtener todas las asignaturas del plan del estudiante
        asignaturas_plan_estudiante = Asignatura.objects.filter(I_PlanID=estudiante.I_PlanID)

        # Obtener todas las asignaturas que tienen prerequisito, es decir, aquellas que están en la tabla AsignaturaPreRequisitos
        asignaturas_con_prerequisito = AsignaturaPreRequisitos.objects.values_list('I_AsignaturaID', flat=True)

        # Filtrar las asignaturas del plan que no tienen prerequisito
        asignaturas_sin_prerequisito = asignaturas_plan_estudiante.exclude(
            I_AsignaturaID__in=asignaturas_con_prerequisito)
        asignaturas_sin_prerequisito = [asignatura.I_AsignaturaID for asignatura in asignaturas_sin_prerequisito]
        print("asignatura sin prerequisitos: ",asignaturas_sin_prerequisito)
        
        asignaturas_sin_prerequisito = [
        asignatura_id for asignatura_id in asignaturas_sin_prerequisito
        if obtener_ciclo_asignatura(asignatura_id) in obtener_ciclos_permitidos(ultimo_semestre_estudiante)
        ]
        # Obtener las asignaturas aprobadas
        asignaturas_aprobadas = HistorialAcademicos.objects.filter(
            N_CodEstudianteID=estudiante, B_AsignaturaAprobada=True
        ).values_list('I_AsignaturaID', flat=True)
        print("asignaturas aprobadas:", list(asignaturas_aprobadas))

        # Obtener asignaturas desaprobadas (por ejemplo, aquellas que no tienen B_AsignaturaAprobada=True)
        asignaturas_desaprobadas = HistorialAcademicos.objects.filter(
            N_CodEstudianteID=estudiante, B_AsignaturaAprobada=False
        ).values_list('I_AsignaturaID', flat=True)
        print("desaprobadas: ",list(asignaturas_desaprobadas))
        
        if len(asignaturas_desaprobadas) >= 4:
            print("El estudiante tiene 4 o más asignaturas desaprobadas. Procesando solo las desaprobadas.")
            ciclos_pares = ["II", "IV", "VI", "VIII", "X"]
            # Lista para almacenar los prerequisitos completos de las asignaturas desaprobadas
            prerequisitos_completos_desaprobadas = []

            # Verificar las asignaturas desaprobadas y extender si son de ciclo impar
            for asignatura_id in asignaturas_desaprobadas:
                asignatura = Asignatura.objects.get(I_AsignaturaID=asignatura_id)
                
                # Si la asignatura está en ciclo impar, se extiende con sus dependientes
                if asignatura.T_Ciclo not in ciclos_pares:
                    prerequisitos_completos_desaprobadas.append(asignatura_id)
                    prerequisitos_dependientes = AsignaturaPreRequisitos.objects.filter(
                        I_PreRequisitoID=asignatura_id
                    ).values_list('I_AsignaturaID', flat=True)
                    prerequisitos_completos_desaprobadas.extend(prerequisitos_dependientes)
                else:
                    # Si la asignatura es ciclo par, no se extiende, solo se agrega
                    prerequisitos_completos_desaprobadas.append(asignatura_id)

            # Resultado final con solo las asignaturas desaprobadas y sus dependientes
            print("Prerequisitos completos con asignaturas desaprobadas: ", list(prerequisitos_completos_desaprobadas))

            # Usar esta lista final para el proceso de programaciones
        
            return agrupar_programaciones(estudiante,prerequisitos_completos_desaprobadas)

        else: 
            # Obtener las asignaturas que dependen de las aprobadas como prerequisitos
            prerequisitos = AsignaturaPreRequisitos.objects.filter(
                I_PreRequisitoID__in=asignaturas_aprobadas
            ).values_list('I_AsignaturaID', flat=True)
            print("prerequisitos:",list(prerequisitos))
            
            prerequisitos = list(prerequisitos)+asignaturas_sin_prerequisito
            print("cursos con pre y sin pre: ",prerequisitos)

            prerequisitos = [asignatura for asignatura in prerequisitos if asignatura not in asignaturas_aprobadas]
            print("prerequisitos 2: ", list(prerequisitos))
            prerequisitos = list(prerequisitos) + list(asignaturas_desaprobadas)
            print('cursos', list(prerequisitos))

            # Definir los ciclos "pares" en números romanos
            ciclos_pares = ["II", "IV", "VI", "VIII", "X"]

            # Lista para almacenar los prerequisitos completos
            prerequisitos_completos = []

            # Lista para almacenar los prerequisitos que no extienden dependientes (ciclo par)
            prerequisitos_sin_extender = []
            
            # Verificar las asignaturas en 'prerequisitos 2' y su ciclo
            for asignatura_id in prerequisitos:
                # Obtener la asignatura para acceder al ciclo
                asignatura = Asignatura.objects.get(I_AsignaturaID=asignatura_id)
                
                # Verificar si el ciclo de la asignatura está en la lista de ciclos "pares"
                if asignatura.T_Ciclo in ciclos_pares:
                    print(f"Asignatura {asignatura_id} pertenece a un ciclo par: {asignatura.T_Ciclo}. No extenderemos dependientes.")
                    # Si está en ciclo par, se agrega a la lista pero no se extiende con dependientes
                    prerequisitos_sin_extender.append(asignatura_id)
                else:
                    # Si no está en ciclo par, agregamos dependientes
                    prerequisitos_completos.append(asignatura_id)
                    # Ahora, extendemos con las asignaturas que dependen de esta asignatura
                    prerequisitos_dependientes = AsignaturaPreRequisitos.objects.filter(
                        I_PreRequisitoID=asignatura_id
                    ).values_list('I_AsignaturaID', flat=True)
                    prerequisitos_completos.extend(prerequisitos_dependientes)

            # Combinar los prerequisitos que no extienden con los que sí lo hacen
            prerequisitos_completos.extend(prerequisitos_sin_extender)

            print("prerequisitos completos (con ciclos pares y sin extender dependientes): ", list(prerequisitos_completos))

            return agrupar_programaciones(estudiante,prerequisitos_completos)

def obtener_ciclo_asignatura(asignatura_id):
    # Obtener la asignatura desde la base de datos
    asignatura = Asignatura.objects.get(I_AsignaturaID=asignatura_id)
    return asignatura.T_Ciclo  # Devuelve el ciclo de la asignatura (por ejemplo "III", "IV", etc.)

def obtener_ciclos_permitidos(ultimo_semestre_estudiante):
    if ultimo_semestre_estudiante == 2:
        return ['I','II',"III", "IV"]  # Ejemplo: solo puede llevar cursos del III y IV ciclo
    elif ultimo_semestre_estudiante == 4:
        return ['I','II',"III", "IV","V", "VI"]
    elif ultimo_semestre_estudiante == 6:
        return ['I','II',"III", "IV","V", "VI","VII", "VIII"]
    elif ultimo_semestre_estudiante == 8:
        return ['I','II',"III", "IV","V", "VI","VII", "VIII","IX", "X"]
    elif ultimo_semestre_estudiante == 0:
        return ['I','II']
    else:
        return []  # Si el semestre es mayor o no está en los casos anteriores, no hay ciclos disponibles


@rol_required("Estudiante")
@usuario_autenticado
def Estudiante_Matricula(request):
    estudiante = obtener_estudiante_desde_sesion(request)
    context_estudiante = datos_estudiante(request)  # Información del estudiante
    programaciones_agrupadas_list = obtener_programaciones_estudiante(estudiante)  # Información de programación

    # Verificar si ya tiene matrícula
    if Matricula.objects.filter(N_CodEstudianteID=estudiante).exists():
        return redirect('estudiante_constancia')

    if request.method == "POST":
        # Llamar a registrar_matricula y verificar si devuelve un JsonResponse con 'status' 
        response = registrar_matricula(request)
        
        # Verificar si el status es "error" (lo obtenemos de los datos del JsonResponse, no del atributo)
        if response.content:
            data = json.loads(response.content.decode("utf-8"))  # Decodificamos el contenido de JSON
            if data.get("status") == "error":
                # Si hay errores, mostrar en la misma página
                return render(request, 'Estudiante/Estudiante_Matricula.html', {
                    **context_estudiante,
                    'programaciones': programaciones_agrupadas_list,
                    'errores': data.get("errores", [])
                })
        
        # Si todo está bien, redirigir a la página de constancia
        return redirect('estudiante_constancia')

    context = {
        **context_estudiante,
        'programaciones': programaciones_agrupadas_list,  # Aquí pasamos la lista correctamente
    }
    return render(request, 'Estudiante/Estudiante_Matricula.html', context)



@rol_required("Estudiante")
@usuario_autenticado
def Programacion_datos(request):
    estudiante = obtener_estudiante_desde_sesion(request)
    programaciones_agrupadas_list = obtener_programaciones_estudiante(estudiante)

    context = {
        'programaciones': programaciones_agrupadas_list
    }
    return context


def registrar_matricula(request):
    if request.method == 'POST':

        # Obtener los IDs de las programaciones seleccionadas como string
        selected_ids_str = request.POST.get("programaciones_seleccionadas", "")

        # Verificar que selected_ids_str no esté vacío
        if selected_ids_str:
            try:
                # Convertir la cadena JSON en una lista de enteros
                selected_ids = json.loads(selected_ids_str)

                # Usar los IDs para realizar la consulta de programaciones
                programaciones_seleccionadas = Programacion.objects.filter(I_ProgramacionID__in=selected_ids)

                # Obtener el estudiante actual (presumiblemente ya autenticado)
                usuario_codigo  = request.session.get("T_NombreUsuario")  # Ajustar según tu lógica de sesión
                estudiante_codigo = usuario_codigo.split('@')[0]  # Ajustar según tu lógica de sesión
                estudiante = get_object_or_404(Estudiante, N_CodEstudianteID=estudiante_codigo)
                errores = validar_matricula(programaciones_seleccionadas, estudiante)
                ultima_matricula = Matricula.objects.order_by('-I_Identificador').first()
                nuevo_identificador = (ultima_matricula.I_Identificador + 1) if ultima_matricula else 1
                
                if errores:
                    return JsonResponse({"status": "error", "errores": errores})  # Errores si los hay

                # Registrar cada programación seleccionada en la tabla de matrícula
                for programacion in programaciones_seleccionadas:
                    try:
                        # Crear una nueva entrada en la tabla de Matricula para cada programación
                        matricula = Matricula(
                            N_CodEstudianteID=estudiante,
                            I_ProgramacionID=programacion,  # Guardamos el objeto Programacion relacionado
                            D_FechaMatricula=timezone.now(),
                            D_DateInsert=timezone.now(),
                            D_DateUpDate=timezone.now(),
                            I_UsuarioID=1,  # El ID del usuario que está realizando la acción, puede ser variable
                            I_Identificador=nuevo_identificador
                        )
                        matricula.save()

                    except Exception as e:
                        print(f"Error al registrar matrícula para Programación ID: {programacion.I_ProgramacionID}. Error: {e}")
                
                return JsonResponse({"status": "success"})
            
            except json.JSONDecodeError:
                print("Error: No se pudo convertir la cadena JSON en una lista.")
            except ValueError:
                print("Error: Algunos de los IDs no son válidos.")
        else:
            print("Error: No se recibieron IDs válidos.")
    
    return JsonResponse({"status": "error", "errores": ["No se recibieron datos de matrícula válidos."]})

@rol_required("Estudiante")
@usuario_autenticado
def Estudiante_Constancia(request):
    """Renderiza la constancia en HTML"""
    estudiante = obtener_estudiante_desde_sesion(request)
    context = obtener_contexto_constancia(estudiante, request)
    return render(request, "Estudiante/Estudiante_Constancia.html", context)

def Estudiante_Constancia_PDF(request):
    """Genera y devuelve la constancia en PDF"""
    estudiante = obtener_estudiante_desde_sesion(request)
    context = obtener_contexto_constancia_pdf(estudiante, request)
    logger.debug(f"Contexto generado: {context}")
    html_string = render_to_string('Estudiante/Estudiante_Constancia_PDF.html', context)
    logger.debug(f"HTML generado: {html_string}")
    pdf_buffer = io.BytesIO()

    try:
        pisa_status = pisa.CreatePDF(html_string, dest=pdf_buffer)
        if pisa_status.err:
            return HttpResponse("Error al generar el PDF", status=500)

        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="constancia_matricula.pdf"'
        response['Cache-Control'] = 'no-store'
        return response
    except Exception as e:
        return HttpResponse(f"Error interno: {e}", status=500)

#def image_to_absolute_path(image_name):
    #return os.path.join(settings.STATIC_ROOT, 'images', image_name)

def obtener_contexto_constancia_pdf(estudiante, request):


    contexto = contexto_pdf_constancia(estudiante, request)
    
    #imagen_logo = image_to_absolute_path('logo.png')

    return {
        **contexto,
        #'imagen_logo': imagen_logo,#ACA
        #'imagen_firma': imagen_firma,#ACA
    }

def contexto_pdf_constancia(estudiante, request):
    """Obtiene los datos de la constancia para reusar en HTML y PDF"""
    context_estudiante = datos_estudiante(request)
    matriculas = Matricula.objects.filter(N_CodEstudianteID=estudiante)
    codigos_liquidacion = list(Pago.objects.filter(N_CodEstudianteID=estudiante).values_list('T_CodLiquidacion', flat=True))
    fecha_pago = list(Pago.objects.filter(N_CodEstudianteID=estudiante).values_list('D_FechaPago', flat=True))
    programaciones_agrupadas = {}
    suma_creditos_por_periodo = {}

    for matricula in matriculas:
        programacion = matricula.I_ProgramacionID
        asignatura_id = programacion.I_AsignaturaID.I_AsignaturaID
        vez_llevado = HistorialAcademicos.objects.filter(
            N_CodEstudianteID=estudiante, 
            I_AsignaturaID=asignatura_id
        ).values_list('I_VezLlevadoAsignatura', flat=True)

        vez_llevado = vez_llevado.first() + 1 if vez_llevado else 1
        periodo = programacion.C_Periodo

        asignatura_info = {
            'periodo': periodo,
            'ciclo': programacion.I_AsignaturaID.T_Ciclo,
            'asignatura': programacion.I_AsignaturaID.T_NombreAsignatura,
            'codigo_asignatura': programacion.I_AsignaturaID.I_CodAsignatura,
            'seccion': programacion.C_Seccion,
            'turno': programacion.C_Turno,
            'aula': programacion.T_Aula,
            'creditos': programacion.I_AsignaturaID.I_Creditos,
            'vez_llevado': vez_llevado,
            'condicion': programacion.I_AsignaturaID.I_CondicionAsignaturaID.T_NombreCondicion,
        }

        key = (programacion.I_AsignaturaID, programacion.C_Seccion)
        if key not in programaciones_agrupadas:
            programaciones_agrupadas[key] = asignatura_info

        if periodo not in suma_creditos_por_periodo:
            suma_creditos_por_periodo[periodo] = 0

        suma_creditos_por_periodo[periodo] += asignatura_info['creditos']

    programaciones_info = sorted(programaciones_agrupadas.values(), key=lambda x: x['periodo'])

    # Extraer períodos únicos y ordenarlos
    periodos_unicos = sorted(set(item['periodo'] for item in programaciones_info))
    identificador = matricula.I_Identificador

    return {
        **context_estudiante,
        'programaciones': programaciones_info,
        'suma_creditos_por_periodo': suma_creditos_por_periodo,
        'suma_creditos_lista': [{'periodo': k, 'creditos': v} for k, v in suma_creditos_por_periodo.items()],
        'fecha_matricula': matriculas.first().D_FechaMatricula if matriculas.exists() else None,
        'periodos': periodos_unicos,  # Lista de períodos únicos para iterar en el template
        'identificador': identificador,
        'liquidacion': codigos_liquidacion,
        'fecha_pago': fecha_pago,
    }



def obtener_contexto_constancia(estudiante, request):
    """Obtiene los datos de la constancia para reusar en HTML y PDF"""
    context_estudiante = datos_estudiante(request)
    matriculas = Matricula.objects.filter(N_CodEstudianteID=estudiante)
    programaciones_agrupadas = {}
    suma_creditos_por_periodo = {}

    for matricula in matriculas:
        programacion = matricula.I_ProgramacionID
        asignatura_id = programacion.I_AsignaturaID.I_AsignaturaID
        vez_llevado = HistorialAcademicos.objects.filter(
            N_CodEstudianteID=estudiante, 
            I_AsignaturaID=asignatura_id
        ).values_list('I_VezLlevadoAsignatura', flat=True)

        vez_llevado = vez_llevado.first() + 1 if vez_llevado else 1
        periodo = programacion.C_Periodo

        asignatura_info = {
            'periodo': periodo,
            'ciclo': programacion.I_AsignaturaID.T_Ciclo,
            'asignatura': programacion.I_AsignaturaID.T_NombreAsignatura,
            'codigo_asignatura': programacion.I_AsignaturaID.I_CodAsignatura,
            'seccion': programacion.C_Seccion,
            'turno': programacion.C_Turno,
            'aula': programacion.T_Aula,
            'creditos': programacion.I_AsignaturaID.I_Creditos,
            'vez_llevado': vez_llevado,
            'condicion': programacion.I_AsignaturaID.I_CondicionAsignaturaID.T_NombreCondicion,
        }

        key = (programacion.I_AsignaturaID, programacion.C_Seccion)
        if key not in programaciones_agrupadas:
            programaciones_agrupadas[key] = asignatura_info

        if periodo not in suma_creditos_por_periodo:
            suma_creditos_por_periodo[periodo] = 0

        suma_creditos_por_periodo[periodo] += asignatura_info['creditos']

    programaciones_info = sorted(programaciones_agrupadas.values(), key=lambda x: x['periodo'])

    return {
        **context_estudiante,
        'programaciones': programaciones_info,
        'suma_creditos_por_periodo': suma_creditos_por_periodo,
        'fecha_matricula': matriculas.first().D_FechaMatricula if matriculas.exists() else None,
    }


def validar_matricula(programaciones_seleccionadas,estudiante):
    # Obtener la categoría del estudiante (quinto superior o regulares)
    if estudiante.B_QuintoSuperior:
        categoria_estudiante = 'QUINTO SUPERIOR'
    else:
        categoria_estudiante = 'REGULAR INVICTO'
    
    # Verificar si la fecha actual está dentro del rango de fechas de matrícula
    if verificarDia(estudiante.B_QuintoSuperior):
        # Verificar que las programaciones seleccionadas tienen cupos disponibles
        for programacion in programaciones_seleccionadas:
            if programacion.I_Cupos <= 0:
                return f"No hay cupos disponibles en la programación de {programacion.I_AsignaturaID.T_NombreAsignatura}."
        for programacion in programaciones_seleccionadas:
            programacion.I_Cupos -= 1
            programacion.save()
        # Si está en el rango, permitir la matrícula
        return None  # Indica que no hay errores, la matrícula puede proceder
    else:
        # Si no está en el rango, mostrar un mensaje de error
        return f"La matrícula para la categoría {categoria_estudiante} está fuera del periodo permitido."


def verificarDia(estudiante_quinto):
    try:
        # Obtener el acceso de matrícula para validar las fechas y la categoría
        acceso_quinto = AccesoMatriculas.objects.first()  # Obtener el primer acceso de matrícula (esto se puede modificar según tu lógica)
        acceso_regular = AccesoMatriculas.objects.all()[1]
        acceso_rezagado = AccesoMatriculas.objects.all()[2]
        # Validación para acceso rezagado
        fecha_inicio_rezagado = datetime.combine(acceso_rezagado.D_DiaApertura, acceso_rezagado.D_HoraApertura)
        fecha_fin_rezagado = datetime.combine(acceso_rezagado.D_DiaCierre, acceso_rezagado.D_HoraCierre)
        if fecha_inicio_rezagado <= datetime.now() <= fecha_fin_rezagado:
            return True
        
        # Validación para acceso quinto superior
        if estudiante_quinto:
            fecha_inicio_quinto = datetime.combine(acceso_quinto.D_DiaApertura, acceso_quinto.D_HoraApertura)
            fecha_fin_quinto = datetime.combine(acceso_quinto.D_DiaCierre, acceso_quinto.D_HoraCierre)
            if fecha_inicio_quinto <= datetime.now() <= fecha_fin_quinto:
                return True
            else:
                return False
        
        # Validación para acceso regular
        fecha_inicio_regular = datetime.combine(acceso_regular.D_DiaApertura, acceso_regular.D_HoraApertura)
        fecha_fin_regular = datetime.combine(acceso_regular.D_DiaCierre, acceso_regular.D_HoraCierre)
        if fecha_inicio_regular <= datetime.now() <= fecha_fin_regular:
            return True
        else:
            return False
    
    except Estudiante.DoesNotExist:
        return False
    except AccesoMatriculas.DoesNotExist:
        return False