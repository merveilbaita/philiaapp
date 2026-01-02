# boutique/forms.py

from decimal import Decimal
from django import forms
from django.forms.models import inlineformset_factory
from django.utils import timezone

from .models import (
    Produit,
    MouvementStock,
    Vente,
    LigneDeVente,
    Paiement,
)

# ----------------------------
# Produits & Mouvements stock
# ----------------------------

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = '__all__'


class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['produit', 'type_mouvement', 'quantite', 'raison', 'date_mouvement']
        widgets = {'date_mouvement': forms.DateInput(attrs={'type': 'date'})}


# ----------------------------
# Ventes
# ----------------------------

class VenteForm(forms.ModelForm):
    """
    Formulaire de création de vente.
    On expose un champ client simple + des champs non-modèle
    pour encaisser un acompte à la création.
    
    ✅ Compatible avec input natif HTML5 datetime-local (sans Flatpickr)
    """
    client_nom = forms.CharField(
        required=False,
        label="Nom du client",
        widget=forms.TextInput(attrs={
            "placeholder": "Ex: Jean Dupont",
            "class": "form-input"
        })
    )

    date_vente = forms.DateTimeField(
        required=True,
        label="Date de la vente",
        widget=forms.DateTimeInput(attrs={
            "type": "datetime-local",  # ← INPUT NATIF HTML5 (fonctionne mobile + desktop)
            "class": "form-input datetime-picker",
        })
    )

    acompte = forms.DecimalField(
        required=False,
        min_value=Decimal('0.00'),
        label="Acompte reçu",
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            "step": "0.01",
            "class": "form-input",
            "placeholder": "0.00"
        })
    )

    MODE_CHOIX = (
        ("ESPECES", "Espèces"),
        ("MOBILE", "Mobile Money"),
        ("BANQUE", "Virement / Carte"),
        ("AUTRE", "Autre"),
    )
    mode_paiement = forms.ChoiceField(
        required=False,
        choices=MODE_CHOIX,
        label="Mode de paiement (acompte)",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Vente
        fields = ['date_vente', 'client_nom']

    def __init__(self, *args, **kwargs):
        """
        Initialise le formulaire avec la date/heure actuelle par défaut.
        Format YYYY-MM-DDTHH:MM requis pour datetime-local.
        """
        super().__init__(*args, **kwargs)
        
        # Ne définir la date par défaut que pour les nouvelles ventes (pas les modifications)
        if not self.instance.pk and not self.initial.get('date_vente'):
            # Format ISO 8601 requis par datetime-local : "2024-01-15T14:30"
            self.initial['date_vente'] = timezone.now().strftime('%Y-%m-%dT%H:%M')

    def clean_acompte(self):
        """Convertit l'acompte en Decimal, ou 0.00 si vide."""
        val = self.cleaned_data.get('acompte')
        if val in (None, ""):
            return Decimal('0.00')
        return Decimal(val)


class LigneDeVenteForm(forms.ModelForm):
    class Meta:
        model = LigneDeVente
        fields = ['produit', 'quantite', 'prix_unitaire_vente']


LigneDeVenteFormSet = inlineformset_factory(
    Vente,
    LigneDeVente,
    form=LigneDeVenteForm,
    extra=3,          # nombre de lignes visibles par défaut
    can_delete=False
)


# ----------------------------
# Paiements additionnels
# ----------------------------

class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['montant', 'mode', 'note']
        widgets = {
            'montant': forms.NumberInput(attrs={"step": "0.01"}),
            'note': forms.TextInput(attrs={"placeholder": "Ex: Règlement partiel, reçu #123"}),
        }
        labels = {
            'montant': 'Montant à encaisser',
            'mode': 'Mode de paiement',
            'note': 'Note (facultatif)',
        }
