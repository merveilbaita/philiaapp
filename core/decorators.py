from django.shortcuts import redirect
from functools import wraps

def role_requis(role_attendu):
    def decorateur(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'profilutilisateur') and request.user.profilutilisateur.role == role_attendu:
                return view_func(request, *args, **kwargs)
            return redirect('dashboard')  # Ou une page "non autorisé"
        return _wrapped_view
    return decorateur
