# TR/decorators.py
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from functools import wraps
from TC.models import UsuarioRoles

# Decorador para verificar si el usuario está autenticado (según las variables de sesión)
def usuario_autenticado(func):
    @wraps(func)
    def _wrapped_view(request, *args, **kwargs):
        # Verifica si las variables de sesión necesarias existen
        if 'I_UsuarioID' not in request.session or 'T_NombreUsuario' not in request.session or 'I_RolID' not in request.session:
            return redirect('login')  # Redirige al login si no está autenticado
        
        # Llama a la vista original
        response = func(request, *args, **kwargs)
        
        # Evitar que la página sea almacenada en caché
        response['Cache-Control'] = 'no-store'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
    return _wrapped_view                

# Decorador para verificar el rol del usuario
def rol_required(rol_nombre):
    def decorator(view_func):
        @usuario_autenticado  # Primero verifica la autenticación
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Verifica el rol del usuario en la sesión
            usuario_rol_id = request.session.get('I_RolID', None)
            
            # Intentamos obtener el nombre del rol de la base de datos
            try:
                # Obtenemos el rol basado en el ID almacenado en la sesión
                rol = UsuarioRoles.objects.get(I_RolID=usuario_rol_id)
                
                # Verificamos si el nombre del rol coincide con el proporcionado
                if rol.T_NombreRol != rol_nombre:
                    return HttpResponseForbidden("No tienes permisos para acceder a esta página.")
            except UsuarioRoles.DoesNotExist:
                return HttpResponseForbidden("Rol no encontrado.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator