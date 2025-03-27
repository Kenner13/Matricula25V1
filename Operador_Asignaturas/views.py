from django.shortcuts import render,redirect,get_object_or_404
from AppLogin.decorators import rol_required,usuario_autenticado 
from Operador_Horarios.views import datos_operador
from TR.models import Programacion
from TI.models import Matricula
from django.shortcuts import render
from datetime import date
from django.shortcuts import render, redirect
from .forms import ProgramacionForm
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages


# Vista protegida para Operadores (solo accesible por usuarios con rol 7)
@rol_required("Operador")
@usuario_autenticado
def operador_asignaturas(request):
    operador_datos = datos_operador(request)
    
    # Obtener las programaciones filtradas por especialidad
    programaciones_filtradas = obtener_programaciones_filtradas(operador_datos["especialidad_id"])
    
    # Filtrar las programaciones por ciclo si es que el operador selecciona uno
    
    ciclo_seleccionado = request.GET.get('ciclo', None)
    if ciclo_seleccionado:
        programaciones_filtradas = filtrar_por_ciclo(programaciones_filtradas, ciclo_seleccionado)
  
    
    # Agrupar las programaciones por asignatura y sección
    programaciones_agrupadas = obtener_programaciones_agrupadas(programaciones_filtradas)
    programaciones_agrupadas_list = convertir_programaciones_a_lista(programaciones_agrupadas)

    paginator = Paginator(programaciones_agrupadas_list, 15)  # 10 items por página
    page_number = request.GET.get('page')  # Obtener el número de la página
    page_obj = paginator.get_page(page_number)

    # Obtener los ciclos disponibles
    ciclos_disponibles = Programacion.objects.values('I_AsignaturaID__T_Ciclo').distinct()

    context = {
        **operador_datos,  # Incluye los datos del operador
        'page_obj': page_obj,  # Agrega las programaciones filtradas
        'ciclos_disponibles': ciclos_disponibles,  # Los ciclos disponibles para filtrar
        'ciclo_seleccionado': ciclo_seleccionado  # El ciclo que fue seleccionado por el operador
    }
    
    return render(request, 'Operador/Operador_Asignaturas.html', context)

def obtener_programaciones_filtradas(especialidad_id):
    # Filtrar las programaciones donde la asignatura tiene la misma especialidad que el operador
    return Programacion.objects.filter(
        I_AsignaturaID__I_PlanID__I_EspecialidadID=especialidad_id
    )

def obtener_programaciones_agrupadas(programaciones_filtradas):
    # Agrupar las programaciones por asignatura y sección
    programaciones_agrupadas = {}
    for programacion in programaciones_filtradas:
        key = (programacion.I_AsignaturaID, programacion.C_Seccion)
        
        # Si la clave no existe, la creamos
        if key not in programaciones_agrupadas:
            matriculados_count = Matricula.objects.filter(I_ProgramacionID=programacion).count()
            programaciones_agrupadas[key] = {
                'ID': programacion.I_ProgramacionID,
                'ciclo': programacion.I_AsignaturaID.T_Ciclo,
                'periodo': programacion.C_Periodo,
                'codigo_asignatura': programacion.I_AsignaturaID.I_CodAsignatura,
                'plan': programacion.I_AsignaturaID.I_PlanID.I_AnioPlan,
                'asignatura': programacion.I_AsignaturaID.T_NombreAsignatura,
                'condicion': programacion.I_AsignaturaID.I_CondicionAsignaturaID.T_NombreCondicion,
                'turno': programacion.C_Turno,
                'creditos': programacion.I_AsignaturaID.I_Creditos,
                'seccion': programacion.C_Seccion,
                'dias': [],
                'horas': [],
                'docentes': f"{programacion.N_CodDocenteID.T_ApelPaterno} {programacion.N_CodDocenteID.T_ApelMaterno} {programacion.N_CodDocenteID.T_Nombre}",
                'aula': programacion.T_Aula,
                'cupos': programacion.I_Cupos,
                'cupos_fijos': programacion.I_CuposFijos,
                'matriculados': matriculados_count 
            }

        # Agregar los días y horarios a las listas
        if programacion.I_DiaID1 and programacion.D_HoraInicio1 and programacion.D_HoraFin1:
            programaciones_agrupadas[key]['dias'].append(programacion.I_DiaID1.T_NombreDia)
            horas1 = f"{programacion.D_HoraInicio1} - {programacion.D_HoraFin1}"
            programaciones_agrupadas[key]['horas'].append(horas1)

        if programacion.I_DiaID2 and programacion.D_HoraInicio2 and programacion.D_HoraFin2:
            programaciones_agrupadas[key]['dias'].append(programacion.I_DiaID2.T_NombreDia)
            horas2 = f"{programacion.D_HoraInicio2} - {programacion.D_HoraFin2}"
            programaciones_agrupadas[key]['horas'].append(horas2)

        if programacion.I_DiaID3 and programacion.D_HoraInicio3 and programacion.D_HoraFin3:
            programaciones_agrupadas[key]['dias'].append(programacion.I_DiaID3.T_NombreDia)
            horas3 = f"{programacion.D_HoraInicio3} - {programacion.D_HoraFin3}"
            programaciones_agrupadas[key]['horas'].append(horas3)


        # Agregar el ID de la programación
        #programaciones_agrupadas[key]['ID'].append(programacion.I_ProgramacionID)

    return programaciones_agrupadas


def convertir_programaciones_a_lista(programaciones_agrupadas):
    # Convertir el diccionario a una lista para enviar al template
    return [
        {
            'ID':  value['ID'],
            'ciclo': value['ciclo'],
            'periodo': value['periodo'],
            'codigo_asignatura': value['codigo_asignatura'],
            'plan': value['plan'],
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
            'cupos_fijos': value['cupos_fijos'],
            'matriculados': value['matriculados']
        }
        for value in programaciones_agrupadas.values()
    ]

@rol_required("Operador")
@usuario_autenticado
def crear_programacion(request):
    # Obtener los datos del operador, incluido el especialidad_id
    operador_datos = datos_operador(request)
    operador_especialidad_id = operador_datos["especialidad_id"]

    if request.method == 'POST':
        # Crear el formulario de Programacion con el operador_especialidad_id
        formulario_programacion = ProgramacionForm(operador_especialidad_id=operador_especialidad_id, data=request.POST)
        
        if formulario_programacion.is_valid():
            # Depuración: Mostrar los datos del formulario antes de guardar
            print("Formulario válido. Los datos enviados son:")
            print(formulario_programacion.cleaned_data)

            # Guardar la programación
            programacion = formulario_programacion.save(commit=False)
            programacion.D_DateInsert = timezone.now().date()  # Fecha de inserción
            programacion.D_DateUpDate = timezone.now().date()  # Fecha de actualización
            programacion.I_UsuarioID = 1 
            programacion.B_Habilitado = 1
            programacion.I_CuposFijos = programacion.I_Cupos
            programacion.save()
            return redirect('operador_asignaturas')  # Redirigir a una página de éxito
        else:
            print("Formulario no válido. Errores:")
    else:
        # Si es un GET, mostrar el formulario vacío
        formulario_programacion = ProgramacionForm(operador_especialidad_id=operador_especialidad_id)

    return render(request, 'Operador/Crear_programacion.html', {**operador_datos,'form': formulario_programacion})


@rol_required("Operador")
@usuario_autenticado
def editar_programacion(request, programacion_id):
    # Obtener los datos del operador
    operador_datos = datos_operador(request)

    # Obtener la programación a editar (o 404 si no existe)
    programacion = get_object_or_404(Programacion, I_ProgramacionID=programacion_id)

    # Si el método es POST, intentamos guardar los datos del formulario
    if request.method == 'POST':
        formulario_programacion = ProgramacionForm(data=request.POST, instance=programacion)

        if formulario_programacion.is_valid():
            # Depuración: Mostrar los datos del formulario antes de guardar
            print("Formulario válido. Los datos enviados son:")
            print(formulario_programacion.cleaned_data)

            # Actualizar los campos de fecha y usuario
            programacion.D_DateUpDate = timezone.now().date()  # Fecha de actualización
            programacion.I_UsuarioID = 1  # Asignar usuario (puede ser dinámico dependiendo de la implementación)
            programacion.I_CuposFijos = programacion.I_Cupos
            
            # Guardar la programación
            formulario_programacion.save()
            return redirect('operador_asignaturas')  # Redirigir a la página de asignaturas del operador
    else:
        # Si es un GET, mostramos el formulario con los datos actuales de la programación
        formulario_programacion = ProgramacionForm(instance=programacion)

    # Renderizar el formulario de edición con los datos del operador y el formulario
    return render(request, 'Operador/Editar_programacion.html', {**operador_datos, 'form': formulario_programacion})

def filtrar_por_ciclo(programaciones, ciclo):
    if ciclo:
        return programaciones.filter(I_AsignaturaID__T_Ciclo=ciclo)
    return programaciones