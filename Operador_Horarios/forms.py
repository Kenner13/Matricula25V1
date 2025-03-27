from django import forms
from TR.models import AccesoMatriculas

class AccesoMatriculasForm(forms.ModelForm):

    class Meta:
        model = AccesoMatriculas
        fields = ['D_HoraApertura', 'D_DiaApertura', 'D_DiaCierre', 'D_HoraCierre', 'T_Categoria']
        widgets = {
            'D_HoraApertura': forms.TimeInput(attrs={'type': 'time'}),
            'D_DiaApertura': forms.DateInput(attrs={'type': 'date'}),
            'D_DiaCierre': forms.DateInput(attrs={'type': 'date'}),
            'D_HoraCierre': forms.TimeInput(attrs={'type': 'time'}),
            'T_Categoria': forms.Select(choices=[('', 'Seleccione una categoría')] + AccesoMatriculas.CATEGORIAS, attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        
        # Si D_HoraApertura o D_HoraCierre son None, asignamos '00:00' por defecto
        hora_apertura = cleaned_data.get('D_HoraApertura')
        hora_cierre = cleaned_data.get('D_HoraCierre')
        if hora_apertura is None:
            cleaned_data['D_HoraApertura'] = '00:00'
        
        if hora_cierre is None:
            cleaned_data['D_HoraCierre'] = '00:00'

        dia_apertura = cleaned_data.get('D_DiaApertura')
        dia_cierre = cleaned_data.get('D_DiaCierre')
        if dia_apertura and dia_cierre:
            if dia_apertura > dia_cierre:
                raise forms.ValidationError('El día de apertura no puede ser mayor al día de cierre.')
            elif dia_apertura == dia_cierre:
                if hora_apertura > hora_cierre:
                    raise forms.ValidationError('La hora de apertura no puede ser mayor a la hora de cierre.')
        return cleaned_data
    
class AccesoMatriculasForm2(forms.ModelForm):
    contrasena = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True, label="Contraseña de administrador")
    class Meta:
        model = AccesoMatriculas
        fields = ['D_HoraApertura', 'D_DiaApertura', 'D_DiaCierre', 'D_HoraCierre', 'T_Categoria']
        widgets = {
            'D_HoraApertura': forms.TimeInput(attrs={'type': 'time'}),
            'D_DiaApertura': forms.DateInput(attrs={'type': 'date'}),
            'D_DiaCierre': forms.DateInput(attrs={'type': 'date'}),
            'D_HoraCierre': forms.TimeInput(attrs={'type': 'time'}),
            'T_Categoria': forms.Select(choices=[('', 'Seleccione una categoría')] + AccesoMatriculas.CATEGORIAS, attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        
        # Si D_HoraApertura o D_HoraCierre son None, asignamos '00:00' por defecto
        hora_apertura = cleaned_data.get('D_HoraApertura')
        hora_cierre = cleaned_data.get('D_HoraCierre')
        if hora_apertura is None:
            cleaned_data['D_HoraApertura'] = '00:00'
        
        if hora_cierre is None:
            cleaned_data['D_HoraCierre'] = '00:00'

        dia_apertura = cleaned_data.get('D_DiaApertura')
        dia_cierre = cleaned_data.get('D_DiaCierre')
        if dia_apertura and dia_cierre:
            if dia_apertura > dia_cierre:
                raise forms.ValidationError('El día de apertura no puede ser mayor al día de cierre.')
            elif dia_apertura == dia_cierre:
                if hora_apertura > hora_cierre:
                    raise forms.ValidationError('La hora de apertura no puede ser mayor a la hora de cierre.')
        return cleaned_data