from django import forms
from .models import Personnel,Prestation
from django.utils import timezone

class PersonnelForm(forms.ModelForm):
    class Meta:
        model = Personnel
        fields = ['nom', 'prenom', 'telephone', 'adresse', 'taux_commission', 'secteur']

DATETIME_LOCAL_FORMAT = "%Y-%m-%dT%H:%M"

class PrestationForm(forms.ModelForm):
    class Meta:
        model = Prestation
        fields = ['personnel', 'secteur', 'service', 'montant_paye', 'date_prestation']
        widgets = {
            'date_prestation': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-input'},
                format=DATETIME_LOCAL_FORMAT
            ),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        # valeur par défaut = maintenant (local)
        if not self.instance.pk and not self.initial.get('date_prestation'):
            now_local = timezone.localtime(timezone.now())
            self.initial['date_prestation'] = now_local.strftime(DATETIME_LOCAL_FORMAT)

    def clean_date_prestation(self):
        value = self.cleaned_data['date_prestation']
        if value is None:
            return value
        # si naïf, rends-le aware dans le fuseau du projet
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.get_current_timezone())
        return value

