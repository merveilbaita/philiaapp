from datetime import timedelta
from datetime import date
from django.db.models import DecimalField
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Sum, Count, Case, When, F, Value, ExpressionWrapper
from django.db.models.functions import Coalesce
from core.models import Depense
from .models import Personnel, Prestation,Commission,Secteur,Service
from core.decorators import role_requis
from .forms import PersonnelForm,PrestationForm
from django.contrib import messages
from decimal import Decimal
from dateutil.relativedelta import relativedelta

@login_required
@role_requis('GESTIONNAIRE_SALON')
@login_required
def dashboard_salon(request):
    # Dates
    today      = timezone.localdate()
    yesterday  = today - timedelta(days=1)

    # 1) Chiffre d'affaires du jour pour HOMMES et FEMMES
    brut_homme  = Prestation.objects.filter(
        date_prestation__date=today,
        secteur__nom='HOMME'
    ).aggregate(total=Sum('montant_paye'))['total'] or Decimal('0')
    brut_femme  = Prestation.objects.filter(
        date_prestation__date=today,
        secteur__nom='FEMME'
    ).aggregate(total=Sum('montant_paye'))['total'] or Decimal('0')

    # 2) Part salon
    revenu_homme = brut_homme * Decimal('0.5')
    revenu_femme = brut_femme * Decimal('0.5')
    revenus_jour = revenu_homme + revenu_femme

    # 3) Même calcul pour hier (pour le %)
    brut_homme_y  = Prestation.objects.filter(
        date_prestation__date=yesterday,
        secteur__nom='HOMME'
    ).aggregate(total=Sum('montant_paye'))['total'] or Decimal('0')
    brut_femme_y  = Prestation.objects.filter(
        date_prestation__date=yesterday,
        secteur__nom='FEMME'
    ).aggregate(total=Sum('montant_paye'))['total'] or Decimal('0')
    revenus_hier = (brut_homme_y * Decimal('0.5')) + (brut_femme_y * Decimal('0.5'))

    # 4) % d'évolution
    if revenus_hier > 0:
        pct_ca = (revenus_jour - revenus_hier) / revenus_hier * 100
    else:
        pct_ca = None

    # 5) Autres KPIs
    total_personnel          = Personnel.objects.count()
    total_prestations_jour   = Prestation.objects.filter(date_prestation__date=today).count()
    # commissions déjà générées
    commissions_homme = Commission.objects.filter(
        prestation__date_prestation__date=today,
        prestation__secteur__nom='HOMME'
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0')
    commissions_femme = Commission.objects.filter(
        prestation__date_prestation__date=today,
        prestation__secteur__nom='FEMME'
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0')

    # 6) Total des dépenses SALON du jour
    depenses_salon_jour = Depense.objects.filter(
        entite='SALON',
        date_depense=today
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0')

    return render(request, 'salon/dashboard.html', {
        'now': timezone.now(),

        # CA salon
        'revenus_jour':         revenus_jour,         # 60% hommes + 50% femmes
        'pct_ca':               pct_ca,               # % vs hier

        # Stats globales
        'total_personnel':      total_personnel,
        'total_prestations_jour': total_prestations_jour,

        # Commissions
        'prestations_homme':    Prestation.objects.filter(
                                    date_prestation__date=today,
                                    secteur__nom='HOMME'
                                ).count(),
        'commissions_homme':    commissions_homme,
        'prestations_femme':    Prestation.objects.filter(
                                    date_prestation__date=today,
                                    secteur__nom='FEMME'
                                ).count(),
        'commissions_femme':    commissions_femme,

        # Dépenses salon
        'depenses_salon_jour':  depenses_salon_jour,
    })



@login_required
@role_requis('GESTIONNAIRE_SALON')
def ajouter_personnel(request):
    if request.method == 'POST':
        form = PersonnelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Personnel ajouté avec succès.")
            return redirect('liste_personnel')
    else:
        form = PersonnelForm()
    return render(request, 'salon/personnel/form.html', {'form': form, 'titre': 'Ajouter un personnel'})

@login_required
def liste_personnel(request):
    personnels = Personnel.objects.select_related('secteur').all()
    return render(request, 'salon/personnel/liste.html', {
        'personnels': personnels
    })


@login_required
@role_requis('GESTIONNAIRE_SALON')
def modifier_personnel(request, pk):
    personnel = get_object_or_404(Personnel, pk=pk)
    if request.method == 'POST':
        form = PersonnelForm(request.POST, instance=personnel)
        if form.is_valid():
            form.save()
            messages.success(request, "Personnel mis à jour avec succès.")
            return redirect('liste_personnel')
    else:
        form = PersonnelForm(instance=personnel)
    return render(request, 'salon/personnel/form.html', {'form': form, 'titre': 'Modifier le personnel'})

@login_required
@role_requis('GESTIONNAIRE_SALON')
def supprimer_personnel(request, pk):
    personnel = get_object_or_404(Personnel, pk=pk)
    if request.method == 'POST':
        personnel.delete()
        messages.success(request, "Personnel supprimé avec succès.")
        return redirect('liste_personnel')
    return render(request, 'salon/personnel/confirm_delete.html', {'personnel': personnel})

@login_required
@role_requis('GESTIONNAIRE_SALON')
def ajouter_prestation(request):
    if request.method == 'POST':
        form = PrestationForm(request.POST)
        if form.is_valid():
            prestation = form.save(commit=False)

            # Assigner automatiquement le secteur du personnel choisi
            prestation.secteur = prestation.personnel.secteur

            prestation.save()  # ✅ Le signal va calculer la commission

            messages.success(request, "Prestation ajoutée avec succès.")
            return redirect('liste_prestations')
    else:
        form = PrestationForm()

    return render(request, 'salon/prestations/form.html', {
        'form': form,
        'titre': 'Ajouter une prestation'
    })

@login_required
@role_requis('GESTIONNAIRE_SALON')
def liste_prestations(request):
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')

    prestations = Prestation.objects.all()

    if date_debut:
        prestations = prestations.filter(date_prestation__date__gte=date_debut)
    if date_fin:
        prestations = prestations.filter(date_prestation__date__lte=date_fin)

    return render(request, 'salon/prestations/liste.html', {
        'prestations': prestations,
        'date_debut': date_debut,
        'date_fin': date_fin,
    })

@login_required
@role_requis('GESTIONNAIRE_SALON')
def liste_commissions(request):
    commissions = Commission.objects.select_related('prestation', 'personnel').order_by('-date_calcul')
    return render(request, 'salon/commissions/liste.html', {
        'commissions': commissions
    })


@login_required
@role_requis('GESTIONNAIRE_SALON')
def rapport_salon(request):
    # 🗓️ Filtres de date
    date_debut = request.GET.get('date_debut')
    date_fin   = request.GET.get('date_fin')

    qs = Prestation.objects.all()
    if date_debut:
        qs = qs.filter(date_prestation__date__gte=date_debut)
    if date_fin:
        qs = qs.filter(date_prestation__date__lte=date_fin)

    # Expressions 60% / 50% pour calcul de la part salon
    expr_homme = ExpressionWrapper(
        F('montant_paye') * Decimal('0.5'),
        output_field=DecimalField(max_digits=12, decimal_places=2)
    )
    expr_femme = ExpressionWrapper(
        F('montant_paye') * Decimal('0.5'),
        output_field=DecimalField(max_digits=12, decimal_places=2)
    )

    part_case = Case(
        When(secteur__nom='HOMME', then=expr_homme),
        When(secteur__nom='FEMME', then=expr_femme),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    part_valeur = Coalesce(part_case, Value(0, output_field=DecimalField()))

    # 1. Montant encaissé (part salon)
    revenu_encaisse = qs.aggregate(
        encaisse=Sum(part_valeur)
    )['encaisse'] or Decimal('0')

    # 2. Total des commissions
    total_commissions = Commission.objects.filter(
        prestation__in=qs
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0')

    # 3. Nombre de prestations
    total_prestations = qs.count()

    # 4. Détail par personnel : NB prestations + MONTANT PAYÉ (pas la commission)
    prestations_par_personnel = qs.values('personnel__nom').annotate(
        nb_prestations=Count('id'),
        montant_total=Sum('montant_paye')   # <-- ICI on somme le prix payé
    ).order_by('-montant_total')

    return render(request, 'salon/rapports/rapport.html', {
        'date_debut':                date_debut,
        'date_fin':                  date_fin,
        'total_prestations':         total_prestations,
        'revenu_encaisse':           revenu_encaisse,
        'total_commissions':         total_commissions,
        'prestations_par_personnel': prestations_par_personnel,
    })


@login_required
@role_requis('GESTIONNAIRE_SALON')
def rapport_commissions_mensuelles(request):
    """
    Affiche les commissions générées sur le mois courant (ou mois sélectionné via GET?mois=MM&annee=YYYY).
    """
    # Lecture des paramètres mois/année, sinon mois courant
    mois = request.GET.get('mois')
    annee = request.GET.get('annee')
    today = timezone.localdate()

    if mois and annee:
        start = date(int(annee), int(mois), 1)
    else:
        start = today.replace(day=1)

    end = (start + relativedelta(months=1)) - relativedelta(days=1)

    # Filtrer SUR le champ DateField date_calcul (pas __date__)
    qs = Commission.objects.filter(
        date_calcul__gte=start,
        date_calcul__lte=end
    )

    total_commissions = qs.aggregate(somme=Sum('montant'))['somme'] or 0

    per_agent = (
        qs
        .values('personnel__nom')
        .annotate(total=Sum('montant'))
        .order_by('-total')
    )

    return render(request, 'salon/rapports/commissions_mensuelles.html', {
        'start': start,
        'end': end,
        'total_commissions': total_commissions,
        'commissions_par_personnel': per_agent,
    })

@login_required
@role_requis('GESTIONNAIRE_SALON')
def rapport_depenses_mensuelles(request):
    mois = request.GET.get('mois')
    annee = request.GET.get('annee')
    today = timezone.localdate()

    if mois and annee:
        start = date(int(annee), int(mois), 1)
    else:
        start = today.replace(day=1)
    end = (start + relativedelta(months=1)) - relativedelta(days=1)

    qs = Depense.objects.filter(
        entite='SALON',
        date_depense__gte=start,
        date_depense__lte=end
    ).order_by('date_depense')

    total_depenses = qs.aggregate(somme=Sum('montant'))['somme'] or 0

    return render(request, 'salon/rapports/depenses_mensuelles.html', {
        'start': start,
        'end': end,
        'depenses': qs,
        'total_depenses': total_depenses,

    })


