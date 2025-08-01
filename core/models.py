from django.db import models
from django.contrib.auth.models import User
from django.db import models



class ProfilUtilisateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('ADMIN', 'Administrateur'),
        ('GESTIONNAIRE_BOUTIQUE', 'Gestionnaire Boutique'),
        ('VENDEUR', 'Vendeur Boutique'),
        ('GESTIONNAIRE_SALON', 'Gestionnaire Salon'),
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Depense(models.Model):
    ENTITE_CHOICES = [
        ('BOUTIQUE','Boutique'),
        ('SALON','Salon'),
    ]
    SECTEUR_CHOICES = [
        ('HOMME','HOMME'),
        ('FEMME','FEMME'),
    ]
    entite = models.CharField(choices=ENTITE_CHOICES, max_length=10)
    description = models.CharField(max_length=255)
    secteur = models.CharField(choices=SECTEUR_CHOICES, max_length=6, null=True, blank=True)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    date_depense = models.DateField(auto_now_add=True)
    justificatif = models.FileField(upload_to='justificatifs/', blank=True, null=True)

    def __str__(self):
        return f"Dépense ({self.entite}): {self.description} - {self.montant} $"