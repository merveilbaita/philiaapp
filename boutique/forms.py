# boutique/forms.py

from django import forms
from .models import Produit, MouvementStock, Vente, LigneDeVente
from django.forms.models import inlineformset_factory

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = '__all__'

class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['produit', 'type_mouvement', 'quantite', 'raison']
        

class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = []

class LigneDeVenteForm(forms.ModelForm):
    class Meta:
        model = LigneDeVente
        fields = ['produit', 'quantite', 'prix_unitaire_vente']

LigneDeVenteFormSet = inlineformset_factory(
    Vente,
    LigneDeVente,
    form=LigneDeVenteForm,
    extra=3,  # nombre de lignes visibles par défaut
    can_delete=False
)
