# salon/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from django.utils import timezone
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


@receiver(post_save, sender=Prestation)
def sync_commission_with_prestation(sender, instance: Prestation, created, **kwargs):
    """
    Crée/met à jour la commission liée à la prestation en utilisant la règle métier.
    - La date de la commission = date de la prestation (même si backdatée).
    - On recalcule le montant de façon sûre (sans .montant_commission).
    """
    # ✅ 1) Déterminer le taux de commission
    #    Essayons d'abord un éventuel champ sur le personnel; sinon règle par défaut.
    taux = getattr(getattr(instance, "personnel", None), "taux_commission", None)
    if taux is None:
        # Ajuste ici si tu as des taux différents par secteur
        if getattr(getattr(instance, "secteur", None), "nom", "") in ("HOMME", "FEMME"):
            taux = Decimal("0.50")
        else:
            taux = Decimal("0.50")  # valeur par défaut

    # ✅ 2) Calcul du montant
    montant_paye = instance.montant_paye or Decimal("0")
    try:
        montant_commission = (montant_paye * Decimal(taux)).quantize(Decimal("0.01"))
    except Exception:
        # si taux n'est pas un Decimal compatible
        montant_commission = (montant_paye * Decimal(str(taux))).quantize(Decimal("0.01"))

    # ✅ 3) Date de calcul = date de la prestation (locale)
    dp = instance.date_prestation
    if dp is None:
        # fallback: aujourd’hui (ne devrait pas arriver si le champ est required)
        calc_date = timezone.localdate()
    else:
        if timezone.is_aware(dp):
            calc_date = dp.astimezone(timezone.get_current_timezone()).date()
        else:
            # dp peut être un DateTimeField naïf ou un DateField
            calc_date = getattr(dp, "date", lambda: dp)()

    # ✅ 4) Upsert de la commission (1 commission par prestation)
    Commission.objects.update_or_create(
        prestation=instance,
        defaults={
            "personnel": instance.personnel,
            "montant": montant_commission,
            "date_calcul": calc_date,
        },
    )