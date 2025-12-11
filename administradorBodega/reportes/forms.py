# reportes/forms.py
from django import forms
from django.utils import timezone

class FiltroReporteForm(forms.Form):
    TIPO_REPORTE_CHOICES = [
        ('prestamos', '📋 Solo Préstamos'),
        ('devoluciones', '🔄 Solo Devoluciones'),
        ('combinado', '📊 Combinado (Préstamos y Devoluciones)'),
    ]
    
    # Filtros generales
    tipo_reporte = forms.ChoiceField(
        choices=TIPO_REPORTE_CHOICES,
        initial='prestamos',
        label='Tipo de Reporte',
        widget=forms.Select(attrs={'class': 'form-select', 'style': 'width: 100%;'})
    )
    
    fecha_desde = forms.DateField(
        required=False,
        label='Fecha Desde',
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-control',
            'style': 'width: 100%;'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        label='Fecha Hasta',
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-control',
            'style': 'width: 100%;'
        })
    )
    
    # Filtros específicos para préstamos
    ESTADO_CHOICES = [
        ('', '📝 Todos los estados'),
        ('PENDIENTE', '⏳ Pendiente'),
        ('ACEPTADA', '✅ Aceptada'),
        ('DEVUELTO_COMPLETO', '🔄 Devuelto completo'),
        ('RECHAZADA', '❌ Rechazada'),
    ]
    
    estado_prestamo = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        required=False,
        label='Estado del Préstamo',
        widget=forms.Select(attrs={'class': 'form-select', 'style': 'width: 100%;'})
    )
    
    # Campo para seleccionar docente
    id_usuario = forms.IntegerField(
        required=False,
        label='ID de Docente (opcional)',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'style': 'width: 100%;',
            'placeholder': 'Ej: 1001'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')
        
        if fecha_desde and fecha_hasta:
            if fecha_desde > fecha_hasta:
                raise forms.ValidationError("❌ La fecha 'Desde' no puede ser mayor que la fecha 'Hasta'")
        
        return cleaned_data