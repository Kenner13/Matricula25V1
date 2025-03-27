from django.shortcuts import render, get_object_or_404, redirect
from TR.models import Operador,AccesoMatriculas
from .forms import AccesoMatriculasForm, AccesoMatriculasForm2
from datetime import date
# Create your views here.
from AppLogin.decorators import rol_required,usuario_autenticado 

from django.contrib import messages
@rol_required("Operador")
@usuario_autenticado
def datos_operador(request):
    # Obtener el código del Operador desde la sesión
    usuario_codigo  = request.session.get("T_NombreUsuario")  # Ajustar según tu lógica de sesión
    operador_codigo = usuario_codigo .split('@')[0]
    #operador_codigo = request.session.get("T:NombreUsuario")
    operador = get_object_or_404(Operador, N_CodOperadorID=operador_codigo)
    especialidad = operador.I_EspecialidadID
    escuela = especialidad.I_EscuelaID
    dependencia = escuela.I_FacultadID
    
    # Contexto con la información solicitada
    context = {
        "codigo_operador": operador.N_CodOperadorID,
        "nombre_operador": f"{operador.T_ApelPaterno} {operador.T_ApelMaterno} {operador.T_Nombre}",
        "especialidad_id": especialidad.I_EspecialidadID,
        "especialidad": especialidad.T_NombreEspecialidad,
        "dependencia": dependencia.T_NombreFacultad,  # Nombre de la dependencia
        "escuela": escuela.T_NombreEscuela,  # Nombre de la escuela
        "escuelaid": escuela.I_EscuelaID
    }
    return context

CONTRASENA_ADMIN = '123456' 

@rol_required("Operador")
@usuario_autenticado
def editar_acceso_matriculas(request, acceso_id):
    acceso_matriculas = get_object_or_404(AccesoMatriculas, I_AccesoID=acceso_id)
    operador_datos = datos_operador(request)
    codOperador = operador_datos['codigo_operador']
    operador_instance = get_object_or_404(Operador, N_CodOperadorID=codOperador)

    if request.method == 'POST':
        form = AccesoMatriculasForm2(request.POST, instance=acceso_matriculas)
        
        # Obtener la contraseña del formulario
        contrasena_ingresada = request.POST.get('contrasena')

        # Verificar si la contraseña es correcta
        if contrasena_ingresada != CONTRASENA_ADMIN:
            return redirect('operador_horarios')

        # Si la contraseña es correcta, proceder con la validación y guardado del formulario
        if form.is_valid():
            categoria = form.cleaned_data['T_Categoria']
            
            # Verificar si ya existe un horario con la misma categoría para este operador
            existing_record = AccesoMatriculas.objects.filter(
                N_CodOperadorID=acceso_matriculas.N_CodOperadorID,
                T_Categoria=categoria
            ).exclude(I_AccesoID=acceso_id).first()  # Excluir el registro actual

            if existing_record:
                # Si existe, mostrar un mensaje de error
                messages.error(request, f"El código {categoria} ya existe para este operador. No se podrá modificar.")
            else:
                acceso_matriculas.N_CodOperadorID = operador_instance  
                acceso_matriculas.D_DateUpDate = date.today()
                # Si no existe, guardar el formulario
                form.save()
                return redirect('operador_horarios')
        else:
            # Si el formulario no es válido, mostrar el error
            messages.error(request, "Hubo un error al guardar los datos.")
    else:
        form = AccesoMatriculasForm2(instance=acceso_matriculas)
    
    context = {
        **operador_datos,
        'form': form,
    }
    return render(request, 'Operador/Editar_Operador_Horarios.html', context)



@rol_required("Operador")
@usuario_autenticado
def operador_horarios(request):
    context_operador = datos_operador(request)
    operador_instance = get_object_or_404(Operador, N_CodOperadorID=context_operador['codigo_operador'])

    # Obtener la especialidad del operador logueado
    especialidad_id = context_operador['especialidad_id']

    # Obtener todos los operadores de la misma especialidad
    operadores_misma_especialidad = Operador.objects.filter(I_EspecialidadID=especialidad_id)

    # Obtener todos los registros de AccesoMatriculas para esos operadores
    horarios = AccesoMatriculas.objects.filter(N_CodOperadorID__in=operadores_misma_especialidad)

    # Verificar si ya existe un horario para alguna categoría
    if request.method == 'POST':
        form = AccesoMatriculasForm(request.POST)
        if form.is_valid():
            categoria = form.cleaned_data['T_Categoria']

            # Verificar si ya existe un horario para esa categoría
            existing_record = AccesoMatriculas.objects.filter(
                N_CodOperadorID=operador_instance,
                T_Categoria=categoria
            ).first()

            if existing_record:
                # Mostrar mensaje de error si el código ya existe
                messages.error(request, f"El código {categoria} ya existe. No se agregará nuevamente.")
            else:
                # Si no existe, guardar el nuevo horario
                acceso_matriculas = form.save(commit=False)
                acceso_matriculas.N_CodOperadorID = operador_instance  # Establecer el operador
                acceso_matriculas.D_DateInsert = date.today()  # Fecha actual para D_DateInsert
                acceso_matriculas.D_DateUpDate = date.today()  # Fecha actual para D_DateUpDate
                acceso_matriculas.I_UsuarioID = 1  # ID del usuario (ajustar según el contexto)
                acceso_matriculas.save()
                # Redirigir para evitar doble envío del formulario
                return redirect('operador_horarios')  # Redirigir para actualizar la vista y listar los horarios

    else:
        form = AccesoMatriculasForm(initial={'N_CodOperadorID': operador_instance})

    context = {
        **context_operador,
        'form': form,
        'horarios': horarios,
    }

    return render(request, 'Operador/Operador_Horarios.html', context)