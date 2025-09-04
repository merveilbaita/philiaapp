# boutique/models.py

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.nom

class Produit(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name='produits')
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_stock = models.PositiveIntegerField(default=0)
    seuil_stock_bas = models.PositiveIntegerField(default=2, help_text="Niveau pour déclencher une alerte", blank=True, null=True  )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.quantite_stock} en stock)"

    def est_en_stock(self):
        """Vérifie si le produit est disponible en stock"""
        return self.quantite_stock > 0
    
    def est_stock_bas(self):
        """Vérifie si le stock est bas selon le seuil défini"""
        return self.quantite_stock <= self.seuil_stock_bas
    
    def marge_brute(self):
        """Calcule la marge brute du produit"""
        return self.prix_vente - self.prix_achat
    
    def marge_pourcentage(self):
        """Calcule le pourcentage de marge"""
        if self.prix_achat > 0:
            return (self.marge_brute() / self.prix_achat) * 100
        return 0
    
    def ajuster_stock(self, quantite, type_mouvement, utilisateur, raison=None, date_mouvement=None, vente=None,):
        """
        Ajuste le stock du produit et crée un mouvement de stock
        
        Args:
            quantite: Nombre d'unités à ajouter/retirer
            type_mouvement: Type de mouvement (ENTREE, SORTIE_VENTE, etc.)
            utilisateur: Utilisateur effectuant l'opération
            raison: Raison du mouvement (optionnel)
        """
        # Vérifier si on peut retirer du stock
        if type_mouvement in ['SORTIE_VENTE', 'AJUSTEMENT_MOINS']:
            if self.quantite_stock < quantite:
                raise ValidationError(f"Stock insuffisant pour {self.nom}. Disponible: {self.quantite_stock}")
            
            # Diminuer le stock
            self.quantite_stock -= quantite
        else:
            # Augmenter le stock
            self.quantite_stock += quantite
        
        # Sauvegarder le produit
        self.save()
        
        # Créer le mouvement de stock
        MouvementStock.objects.create(
            produit=self,
            type_mouvement=type_mouvement,
            quantite=quantite,
            utilisateur=utilisateur,
            raison=raison,
            date_mouvement=date_mouvement or timezone.localdate(),
            vente=vente
        )
        
        return True

class Vente(models.Model):
    STATUT_PAYEE = 'PAYEE'
    STATUT_PARTIELLE = 'PARTIELLE'
    STATUT_IMPAYEE = 'IMPAYEE'
    STATUT_CHOIX = [
        (STATUT_PAYEE, 'Payée'),
        (STATUT_PARTIELLE, 'Partiellement payée'),
        (STATUT_IMPAYEE, 'Impayée'),
    ]

    client_nom = models.CharField(max_length=200, blank=True, null=True)
    vendeur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    date_vente = models.DateTimeField(default=timezone.now())
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # = valeur brute de la vente
    est_complete = models.BooleanField(default=False, help_text="Indique si la vente est finalisée")
    montant_encaisse = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    statut = models.CharField(max_length=12, choices=STATUT_CHOIX, default=STATUT_IMPAYEE)
    # optionnel : un nom client simple si tu n’as pas de modèle Client
    client_nom = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = "Vente"
        verbose_name_plural = "Ventes"
        ordering = ['-date_vente']

    def __str__(self):
        return f"Vente #{self.id} du {self.date_vente.strftime('%d/%m/%Y')}"
    

    @property
    def nom_client(self) -> str:
        """Nom du client prêt à afficher (fallback si vide)."""
        nom = (self.client_nom or "").strip()
        return nom if nom else "Client comptant"

    def calculer_total(self):
        total = sum(ligne.prix_unitaire_vente * ligne.quantite for ligne in self.lignes.all())
        self.total = total
        self.save(update_fields=["total"])
        return total

    def finaliser(self):
        if self.est_complete:
            return False
        for ligne in self.lignes.all():
            ligne.produit.ajuster_stock(
                quantite=ligne.quantite,
                type_mouvement='SORTIE_VENTE',
                utilisateur=self.vendeur,
                raison=f"Vente #{self.id}",
                date_mouvement = self.date_vente.date(),
            )
        self.est_complete = True
        self._maj_statut()   # met à jour en fonction de montant_encaisse
        self.save(update_fields=["est_complete", "statut"])
        return True

    @property
    def reste_a_payer(self):
        return (self.total or Decimal('0')) - (self.montant_encaisse or Decimal('0'))

    def _maj_statut(self):
        if self.montant_encaisse >= self.total:
            self.statut = self.STATUT_PAYEE
        elif self.montant_encaisse > 0:
            self.statut = self.STATUT_PARTIELLE
        else:
            self.statut = self.STATUT_IMPAYEE

    def enregistrer_paiement(self, montant, utilisateur=None, mode="ESPECES", note=""):
        """Ajoute un paiement et met à jour l’encaissement + statut."""
        if montant <= 0:
            raise ValidationError("Le montant du paiement doit être positif.")
        Paiement.objects.create(
            vente=self,
            montant=montant,
            mode=mode,
            enregistre_par=utilisateur,
            note=note
        )
        self.montant_encaisse = (self.montant_encaisse or Decimal('0')) + Decimal(montant)
        self._maj_statut()
        self.save(update_fields=["montant_encaisse", "statut"])


class LigneDeVente(models.Model):
    vente = models.ForeignKey(Vente, related_name='lignes', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField()
    prix_unitaire_vente = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Ligne de vente"
        verbose_name_plural = "Lignes de vente"
    
    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"
    
    def clean(self):
        """Valide que le stock est suffisant"""
        if self.quantite > self.produit.quantite_stock:
            raise ValidationError(f"Stock insuffisant pour {self.produit.nom}. Disponible: {self.produit.quantite_stock}")
    
    def sous_total(self):
        """Calcule le sous-total de la ligne"""
        return self.prix_unitaire_vente * self.quantite
    
class Paiement(models.Model):
    MODE_CHOIX = [
        ("ESPECES", "Espèces"),
        ("MOBILE", "Mobile Money"),
        ("BANQUE", "Virement / Carte"),
        ("AUTRE", "Autre"),
    ]
    vente = models.ForeignKey(Vente, related_name="paiements", on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode = models.CharField(max_length=10, choices=MODE_CHOIX, default="ESPECES")
    date_paiement = models.DateTimeField(auto_now_add=True)
    enregistre_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-date_paiement']

    def __str__(self):
        return f"Paiement {self.montant} sur vente #{self.vente_id}"

class MouvementStock(models.Model):
    """ Pour l'historique des mouvements de stock """
    TYPE_MOUVEMENT = (
        ('ENTREE', 'Entrée de stock'),
        ('SORTIE_VENTE', 'Sortie pour vente'),
        ('AJUSTEMENT_PLUS', 'Ajustement manuel (+)'),
        ('AJUSTEMENT_MOINS', 'Ajustement manuel (-)'),
    )
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='mouvements')
    type_mouvement = models.CharField(max_length=20, choices=TYPE_MOUVEMENT)
    quantite = models.PositiveIntegerField()
    date_mouvement = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    raison = models.TextField(blank=True, null=True, help_text="Ex: Vente #123, Inventaire annuel")
    date_mouvement=models.DateField(default=timezone.localdate())
    created_at= models.DateTimeField(auto_now_add=True)
    vente = models.ForeignKey("Vente", null=True,blank=True, on_delete=models.SET_NULL, related_name="mouvements_stock")

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-date_mouvement']

    def __str__(self):
        return f"{self.produit.nom} : {self.quantite} ({self.get_type_mouvement_display()})"