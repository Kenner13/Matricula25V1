from django import forms
from TR.models import Programacion, Asignatura

class ProgramacionForm(forms.ModelForm):
    operador_especialidad_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Programacion
        fields = [
            'I_AsignaturaID', 'C_Periodo', 'C_Turno', 'C_Seccion',
            'I_DiaID1', 'D_HoraInicio1', 'D_HoraFin1',
            'I_DiaID2', 'D_HoraInicio2', 'D_HoraFin2',
            'I_DiaID3', 'D_HoraInicio3', 'D_HoraFin3',
            'N_CodDocenteID', 'T_Aula', 'I_Cupos'
        ]

    def __init__(self, *args, **kwargs):
        operador_especialidad_id = kwargs.pop('operador_especialidad_id', None)
        super().__init__(*args, **kwargs)

        if operador_especialidad_id:
            self.fields['I_AsignaturaID'].queryset = Asignatura.objects.filter(I_PlanID__I_EspecialidadID=operador_especialidad_id)

        # Personalización de Labels
        self.fields['I_AsignaturaID'].label = "Asignatura"
        self.fields['C_Periodo'].label = "Periodo"
        self.fields['C_Turno'].label = "Turno"
        self.fields['C_Seccion'].label = "Sección"
        self.fields['I_DiaID1'].label = "Día 1"
        self.fields['D_HoraInicio1'].label = "Hora Inicio 1"
        self.fields['D_HoraFin1'].label = "Hora Fin 1"
        self.fields['I_DiaID2'].label = "Día 2"
        self.fields['D_HoraInicio2'].label = "Hora Inicio 2"
        self.fields['D_HoraFin2'].label = "Hora Fin 2"
        self.fields['I_DiaID3'].label = "Día 3"
        self.fields['D_HoraInicio3'].label = "Hora Inicio 3"
        self.fields['D_HoraFin3'].label = "Hora Fin 3"
        self.fields['N_CodDocenteID'].label = "Docente"
        self.fields['T_Aula'].label = "Aula"
        self.fields['I_Cupos'].label = "Cupos"

        # Personalización de Widgets para campos de hora
        self.fields['D_HoraInicio1'].widget = forms.TimeInput(attrs={'type': 'time'})
        self.fields['D_HoraFin1'].widget = forms.TimeInput(attrs={'type': 'time'})
        self.fields['D_HoraInicio2'].widget = forms.TimeInput(attrs={'type': 'time'})
        self.fields['D_HoraFin2'].widget = forms.TimeInput(attrs={'type': 'time'})
        self.fields['D_HoraInicio3'].widget = forms.TimeInput(attrs={'type': 'time'})
        self.fields['D_HoraFin3'].widget = forms.TimeInput(attrs={'type': 'time'})

    # Validaciones personalizadas si es necesario
    def clean_C_Periodo(self):
        periodo = self.cleaned_data.get('C_Periodo')
        if len(periodo) > 2:
            raise forms.ValidationError("El periodo debe tener 2 caracteres.")
        return periodo

    def clean_I_Cupos(self):
        cupos = self.cleaned_data.get('I_Cupos')
        if cupos < 0:
            raise forms.ValidationError("Los cupos deben ser mayores que 0.")
        return cupos

    def clean(self):
        cleaned_data = super().clean()

        # Recuperamos los valores de los días y horas de inicio y fin
        dia1 = cleaned_data.get('I_DiaID1')
        inicio1 = cleaned_data.get('D_HoraInicio1')
        fin1 = cleaned_data.get('D_HoraFin1')

        dia2 = cleaned_data.get('I_DiaID2')
        inicio2 = cleaned_data.get('D_HoraInicio2')
        fin2 = cleaned_data.get('D_HoraFin2')

        dia3 = cleaned_data.get('I_DiaID3')
        inicio3 = cleaned_data.get('D_HoraInicio3')
        fin3 = cleaned_data.get('D_HoraFin3')

        # Comprobamos si hay coincidencias de horarios en los días asignados, ignorando None
        if dia1 and dia2 and dia1 == dia2:  # Solo si ambos días están seleccionados
            if inicio1 and fin1 and inicio2 and fin2 and not self._no_overlap(inicio1, fin1, inicio2, fin2):
                raise forms.ValidationError("Los horarios del Día 1 y Día 2 se superponen.")
        
        if dia1 and dia3 and dia1 == dia3:  # Solo si ambos días están seleccionados
            if inicio1 and fin1 and inicio3 and fin3 and not self._no_overlap(inicio1, fin1, inicio3, fin3):
                raise forms.ValidationError("Los horarios del Día 1 y Día 3 se superponen.")
        
        if dia2 and dia3 and dia2 == dia3:  # Solo si ambos días están seleccionados
            if inicio2 and fin2 and inicio3 and fin3 and not self._no_overlap(inicio2, fin2, inicio3, fin3):
                raise forms.ValidationError("Los horarios del Día 2 y Día 3 se superponen.")

        return cleaned_data

    def _no_overlap(self, start1, end1, start2, end2):
        """
        Verifica si dos rangos de tiempo se superponen.
        """
        if start1 >= end2 or start2 >= end1:
            return True  # No se superponen
        return False  # Se superponen