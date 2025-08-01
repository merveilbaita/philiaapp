# salon/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from .models import Prestation, Commission

@receiver(post_save, sender=Prestation)
def calculer_commission(sender, instance, created, **kwargs):
    """
    Signal qui calcule la commission chaque fois qu'une Prestation est sauvegardée.
    Utilise update_or_create pour éviter les doublons.
    """

    prestation = instance
    personnel = prestation.personnel
    secteur = personnel.secteur

    # Le taux de commission peut venir du secteur ou du personnel
    taux_commission = personnel.taux_commission or secteur.taux_commission

    # Sécuriser avec Decimal pour éviter erreurs de type
    montant_commission = prestation.montant_paye * Decimal(str(taux_commission))

    # update_or_create garantit qu'une seule commission existe pour la prestation
    Commission.objects.update_or_create(
        prestation=prestation,
        defaults={
            'personnel': personnel,
            'montant': montant_commission
        }
    )

    print(f"✅ Commission calculée : {montant_commission} pour la prestation {prestation.id}")
