from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from boutique.models import Produit, Vente
from salon.models import Prestation, Commission
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import ConnexionHistorique


@receiver(post_migrate)
def creer_groupes_roles(sender, **kwargs):
    # 1. Administrateur (tous les droits) – pas besoin de groupe spécial si superuser
    # 2. Gestionnaire Boutique
    groupe_boutique, _ = Group.objects.get_or_create(name="Gestionnaire Boutique")
    # Donner toutes les permissions sur Produit, Vente
    permissions_boutique = Permission.objects.filter(content_type__app_label='boutique')
    groupe_boutique.permissions.set(permissions_boutique)

    # 3. Vendeur
    groupe_vendeur, _ = Group.objects.get_or_create(name="Vendeur")
    perms_vendeur = Permission.objects.filter(
        content_type__app_label='boutique',
        codename__in=['add_vente', 'view_vente', 'view_produit']
    )
    groupe_vendeur.permissions.set(perms_vendeur)

    # 4. Gestionnaire Salon
    groupe_salon, _ = Group.objects.get_or_create(name="Gestionnaire Salon")
    permissions_salon = Permission.objects.filter(content_type__app_label='salon')
    groupe_salon.permissions.set(permissions_salon)

    print("✅ Groupes et permissions configurés.")


def get_client_ip(request):
    # si t'es derrière un proxy (Render), tu peux considérer X-Forwarded-For avec précaution
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    ConnexionHistorique.objects.create(
        user=user,
        event=ConnexionHistorique.EVENT_LOGIN,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
        session_key=request.session.session_key,
    )

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    ConnexionHistorique.objects.create(
        user=user,
        event=ConnexionHistorique.EVENT_LOGOUT,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
        session_key=request.session.session_key,
    )

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    # credentials may include username
    user = None
    UserModel = get_user_model()
    username = credentials.get('username')
    if username:
        try:
            user = UserModel.objects.get(**{UserModel.USERNAME_FIELD: username})
        except UserModel.DoesNotExist:
            user = None

    ConnexionHistorique.objects.create(
        user=user,
        event=ConnexionHistorique.EVENT_FAILED,
        ip_address=get_client_ip(request) if request else "",
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000] if request else "",
        note=f"Tentative pour '{username}'",
    )
