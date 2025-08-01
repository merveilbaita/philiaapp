from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from boutique.models import Produit, Vente
from salon.models import Prestation, Commission

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
