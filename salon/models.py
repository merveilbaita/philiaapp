from django.db import models
from django.conf import settings
from decimal import Decimal


class Secteur(models.Model):
    NOM_CHOICES = [
        ('HOMME', 'Homme'),
        ('FEMME', 'Femme'),
    ]

    nom = models.CharField(max_length=20, choices=NOM_CHOICES, unique=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Le responsable est un utilisateur du système
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='secteurs_responsables'  # Ajout d'un related_name explicite pour éviter les conflits
    )
    taux_commission = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Ex: 0.50 pour 50%"
    )

    def __str__(self):
        return f"Secteur {self.get_nom_display()} - Resp: {self.responsable.get_full_name() if self.responsable else 'Aucun'}"

class Personnel(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    taux_commission = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.30,
        help_text="Ex: 0.30 pour 30%"
    )
    secteur = models.ForeignKey(Secteur, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.secteur.nom})"


class Service(models.Model):
    nom = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    duree_estimee = models.DurationField(help_text="Format: HH:MM:SS")

    def __str__(self):
        return f"{self.nom} - {self.prix} CDF"

class Prestation(models.Model):
    personnel = models.ForeignKey(Personnel, on_delete=models.PROTECT)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    secteur = models.ForeignKey(Secteur, on_delete=models.PROTECT)
    date_prestation = models.DateTimeField(auto_now_add=True)
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.service.nom} ({self.secteur.nom}) par {self.personnel} le {self.date_prestation.strftime('%d/%m/%Y')}"

class Commission(models.Model):
    prestation = models.OneToOneField(Prestation, on_delete=models.CASCADE)
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_calcul = models.DateField(auto_now_add=True)
    est_payee = models.BooleanField(default=False)

    def __str__(self):
        return f"Commission pour {self.personnel} - {self.montant} CDF"