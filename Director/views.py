from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from AppLogin.decorators import rol_required,usuario_autenticado 
from TI.models import Matricula
# Create your views here.
@rol_required("Director")
@usuario_autenticado
def eliminar_matricula(request):
    if request.method == 'POST':
        # Obtener el código del estudiante desde el formulario
        codigo_estudiante = request.POST.get('codigo_estudiante')

        # Verificar si el código es válido
        if not codigo_estudiante:
            messages.error(request, "Por favor ingrese el código del estudiante.")
            return redirect('eliminar_matricula')  # Cambia a la vista correcta

        # Buscar todas las matrículas del estudiante
        matriculas = Matricula.objects.filter(N_CodEstudianteID__N_CodEstudianteID=codigo_estudiante)
        
        # Si no hay matrículas para ese estudiante
        if not matriculas.exists():
            messages.error(request, f"No se encontró ninguna matrícula para el estudiante con código {codigo_estudiante}.")
            return redirect('eliminar_matricula')

        # Aumentar los cupos en cada programación asociada a las matrículas
        for matricula in matriculas:
            programacion = matricula.I_ProgramacionID
            programacion.I_Cupos += 1
            programacion.save()

        # Eliminar todas las matrículas del estudiante
        matriculas.delete()

        # Mensaje de éxito
        messages.success(request, f"Todas las matrículas del estudiante con código {codigo_estudiante} han sido eliminadas y los cupos correspondientes han sido aumentados.")
        return redirect('eliminar_matricula')  # Redirige a la vista correspondiente

    return render(request, 'Director/Eliminar_Matricula.html')
