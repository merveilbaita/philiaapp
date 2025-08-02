from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings



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
    


class ConnexionHistorique(models.Model):
    EVENT_LOGIN = "login"
    EVENT_LOGOUT = "logout"
    EVENT_FAILED = "failed"
    EVENT_CHOICES = [
        (EVENT_LOGIN, "Connexion réussie"),
        (EVENT_LOGOUT, "Déconnexion"),
        (EVENT_FAILED, "Échec de connexion"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    event = models.CharField(max_length=10, choices=EVENT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)  # support IPv6
    user_agent = models.TextField(blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    note = models.TextField(blank=True, null=True)  # ex: raison échec

    class Meta:
        verbose_name = "Historique de connexion"
        verbose_name_plural = "Historique de connexions"
        ordering = ['-timestamp']

    def __str__(self):
        user_repr = self.user.username if self.user else "Inconnu"
        return f"{user_repr} {self.get_event_display()} à {self.timestamp}"
