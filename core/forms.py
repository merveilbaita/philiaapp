from django import forms
from django.contrib.auth.models import User
from core.models import ProfilUtilisateur, Depense
from django.contrib.auth.forms import AuthenticationForm

class InscriptionForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ProfilUtilisateur.ROLE_CHOICES, label="Rôle")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']


class ConnexionForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur", 'class': 'form-control'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': "Mot de passe", 'class': 'form-control'})
    )

# core/forms.py
class DepenseForm(forms.ModelForm):
    class Meta:
        model = Depense
        fields = ['secteur', 'description','montant','justificatif']
