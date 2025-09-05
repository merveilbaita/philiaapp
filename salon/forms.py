from django import forms
from .models import Personnel,Prestation

class PersonnelForm(forms.ModelForm):
    class Meta:
        model = Personnel
        fields = ['nom', 'prenom', 'telephone', 'adresse', 'taux_commission', 'secteur']

class PrestationForm(forms.ModelForm):
    class Meta:
        model = Prestation
        fields = ['personnel', 'service', 'montant_paye', 'date_prestation']

