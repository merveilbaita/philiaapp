from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from core.models import Depense, ProfilUtilisateur
from .models import ConnexionHistorique

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


@admin.register(ConnexionHistorique)
class ConnexionHistoriqueAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'timestamp', 'ip_address', 'session_key')
    list_filter = ('event', 'timestamp', 'user')
    search_fields = ('user__username', 'ip_address', 'note')
    readonly_fields = ('user', 'event', 'timestamp', 'ip_address', 'user_agent', 'session_key', 'note')
    ordering = ('-timestamp',)

