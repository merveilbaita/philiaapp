# boutique/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import MouvementStock, Vente, LigneDeVente

@receiver(post_save, sender=MouvementStock)
def verifier_stock_bas(sender, instance, created, **kwargs):
    """
    Vérifie si le stock est bas après un mouvement et envoie une alerte si nécessaire.
    Note: La mise à jour du stock est maintenant gérée par la méthode ajuster_stock() du modèle Produit.
    """
    if created:
        produit = instance.produit
        
        # Vérifier le seuil (sans modifier le stock qui est déjà géré)
        if produit.est_stock_bas():
            # ENVOYER UNE NOTIFICATION
            message = f"ALERTE: Le stock de '{produit.nom}' est bas ({produit.quantite_stock}/{produit.seuil_stock_bas})!"
            print(message)  # Pour le développement/debug
            
            # Créer une notification dans la base de données (si vous avez un modèle Notification)
            # Notification.objects.create(
            #     message=message,
            #     type="STOCK_BAS",
            #     produit=produit
            # )
            
            # Envoyer un email (décommentez pour activer)
            # if hasattr(settings, 'EMAIL_NOTIFICATIONS_ENABLED') and settings.EMAIL_NOTIFICATIONS_ENABLED:
            #     send_mail(
            #         f'Alerte stock bas: {produit.nom}',
            #         message,
            #         settings.DEFAULT_FROM_EMAIL,
            #         [settings.ADMIN_EMAIL],
            #         fail_silently=True,
            #     )

@receiver(post_save, sender=LigneDeVente)
def mettre_a_jour_total_vente(sender, instance, created, **kwargs):
    """Met à jour le total de la vente quand une ligne est ajoutée/modifiée"""
    instance.vente.calculer_total()

