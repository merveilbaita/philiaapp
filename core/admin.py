from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from core.models import Depense, ProfilUtilisateur

# Étendre l'affichage dans admin
class ProfilUtilisateurInline(admin.StackedInline):
    model = ProfilUtilisateur
    can_delete = False
    verbose_name_plural = 'Profil Utilisateur'

# D'abord désenregistrer User
admin.site.unregister(User)

# Puis le réenregistrer avec notre version
@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    inlines = (ProfilUtilisateurInline,)

admin.site.register(Depense)
