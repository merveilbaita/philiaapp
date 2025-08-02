from decimal import Decimal
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib.auth import login

from salon.models import Prestation
from .forms import InscriptionForm, ConnexionForm,DepenseForm
from core.models import ProfilUtilisateur,Depense
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime
from boutique.models import Categorie, LigneDeVente, Produit, Vente
from django.db.models import Sum, F,DecimalField, ExpressionWrapper
from django.utils import timezone


now = timezone.now()

def inscription_view(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            # Créer l'utilisateur
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Créer le profil
            role = form.cleaned_data['role']
            profil = ProfilUtilisateur.objects.get(user=user)
            profil.role = role
            profil.save()

            # Ajouter au groupe correspondant
            group = Group.objects.get(name=profil.get_role_display())
            user.groups.add(group)

            login(request, user)  # Connexion automatique
            return redirect('connexion')  # Redirige vers la page d'accueil (à créer)
    else:
        form = InscriptionForm()

    return render(request, 'core/inscription.html', {'form': form})


def connexion_view(request):
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                try:
                    profil = ProfilUtilisateur.objects.get(user=user)
                except ProfilUtilisateur.DoesNotExist:
                    messages.error(request, "Profil utilisateur introuvable.")
                    return redirect('connexion')

                login(request, user)

                # Redirection selon le rôle de l'utilisateur
                role = profil.role
                if role == 'ADMIN':
                    return redirect('creer_vente')  # Dashboard global pour Admin
                elif role == 'GESTIONNAIRE_BOUTIQUE':
                    return redirect('dashboard')  # Même dashboard pour l’instant
                elif role == 'VENDEUR':
                    return redirect('dashboard')  # Vers dashboard correspondant
                elif role == 'GESTIONNAIRE_SALON':
                    return redirect('dashboard_salon')  # Même ici, à adapter plus tard

                else:
                    messages.error(request, "Rôle utilisateur non reconnu.")
                    return redirect('connexion')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = ConnexionForm()

    return render(request, 'core/connexion.html', {'form': form})

def deconnexion_view(request):
    logout(request)
    return redirect('connexion')  # 



@login_required
def dashboard_view(request):
    # Date du jour en local
    aujourdhui = timezone.localdate()

    profil = ProfilUtilisateur.objects.get(user=request.user)
    is_admin = (profil.role == 'ADMIN')

    # 1) Ventes finalisées du jour
    ventes_du_jour = Vente.objects.filter(
        date_vente__date=aujourdhui,
        est_complete=True
    )
    lignes_du_jour = LigneDeVente.objects.filter(vente__in=ventes_du_jour)

    # 2) Recette brute (CA)
    recette_brute_jour = lignes_du_jour.aggregate(
        total_ca=Sum(
            ExpressionWrapper(
                F('prix_unitaire_vente') * F('quantite'),
                output_field=DecimalField()
            )
        )
    )['total_ca'] or Decimal('0')

    # 3) Coût d’achat (approvisionnement)
    cout_approvisionnement_jour = lignes_du_jour.aggregate(
        total_cout=Sum(
            ExpressionWrapper(
                F('produit__prix_achat') * F('quantite'),
                output_field=DecimalField()
            )
        )
    )['total_cout'] or Decimal('0')

    # 4) Marge brute
    marge_brute_jour = recette_brute_jour - cout_approvisionnement_jour

    # 5) Dépenses BOUTIQUE du jour
    depenses_boutique_jour = Depense.objects.filter(
        entite='BOUTIQUE',
        date_depense=aujourdhui
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0')

    # 6) Revenu net
    revenu_net_jour = marge_brute_jour - depenses_boutique_jour

    # ----- reste de vos stats -----

    # Valeur de stock et catégories
    produits = Produit.objects.all().annotate(
        valeur_stock=ExpressionWrapper(
            F('prix_achat') * F('quantite_stock'),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    )
    total_approvisionnement = produits.aggregate(total=Sum('valeur_stock'))['total'] or Decimal('0')
    categories = Categorie.objects.annotate(
        valeur_stock=Sum(
            ExpressionWrapper(
                F('produits__prix_achat') * F('produits__quantite_stock'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
    )
    top_produits = produits.order_by('-valeur_stock')[:5]
    total_produits = produits.count()
    stock_faible = produits.filter(quantite_stock__lte=F('seuil_stock_bas')).count()

    # Revenus du mois
    mois = aujourdhui.month
    annee = aujourdhui.year
    ventes_mois = Vente.objects.filter(date_vente__month=mois, date_vente__year=annee, est_complete=True)
    revenus_mois = ventes_mois.aggregate(total=Sum('total'))['total'] or Decimal('0')

    return render(request, "core/dashboard.html", {
        # résumé financier
        'is_admin': is_admin,
        'recette_brute_jour': recette_brute_jour,
        'cout_approvisionnement_jour': cout_approvisionnement_jour,
        'marge_brute_jour': marge_brute_jour,
        'depenses_boutique_jour': depenses_boutique_jour,
        'revenu_net_jour': revenu_net_jour,

        # stats stock & ventes
        'total_approvisionnement': total_approvisionnement,
        'categories': categories,
        'top_produits': top_produits,
        'total_produits': total_produits,
        'ventes_jour': ventes_du_jour.count(),
        'stock_faible': stock_faible,
        'revenus_mois': revenus_mois,
    })




@login_required
def liste_depenses(request):
    depenses = Depense.objects.order_by('-date_depense')
    return render(request, 'core/depenses/liste.html', {'depenses': depenses})

@login_required
def ajouter_depense(request):
    if request.method == 'POST':
        form = DepenseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Dépense enregistrée avec succès.")
            return redirect('liste_depenses')
    else:
        form = DepenseForm()
    
    return render(request, 'core/depenses/ajouter.html', {'form': form})

# ✅ Liste pour la BOUTIQUE

@login_required
def liste_depenses_boutique(request):
    profil = ProfilUtilisateur.objects.get(user=request.user)
    if profil.role != 'GESTIONNAIRE_BOUTIQUE' and profil.role != 'ADMIN':
        return HttpResponseForbidden("Vous n'avez pas la permission d'accéder aux dépenses de la boutique.")
    
    depenses = Depense.objects.filter(entite='BOUTIQUE').order_by('-date_depense')
    return render(request, 'core/depenses/liste_boutique.html', {'depenses': depenses})

# ✅ Liste pour le SALON
@login_required
def liste_depenses_salon(request):
    profil = ProfilUtilisateur.objects.get(user=request.user)
    if profil.role != 'GESTIONNAIRE_SALON' and profil.role != 'ADMIN':
        return HttpResponseForbidden("Vous n'avez pas la permission d'accéder aux dépenses du salon.")
    
    depenses = Depense.objects.filter(entite='SALON').order_by('-date_depense')
    return render(request, 'core/depenses/liste_salon.html', {'depenses': depenses})


# ✅ Ajouter pour la BOUTIQUE

@login_required
def ajouter_depense_boutique(request):
    # 🔒 Contrôle d’accès
    profil = request.user.profilutilisateur
    if profil.role not in ('GESTIONNAIRE_BOUTIQUE', 'ADMIN'):
        return HttpResponseForbidden("Vous n'avez pas la permission d'ajouter une dépense pour la boutique.")

    # date du jour en local
    aujourdhui = timezone.localdate()

    # 🔍 Recette brute du jour (CA)
    ventes_du_jour = Vente.objects.filter(
        date_vente__date=aujourdhui,
        est_complete=True
    )
    recette_brute_jour = ventes_du_jour.aggregate(total=Sum('total'))['total'] or Decimal('0')

    # 🔍 Dépenses déjà enregistrées aujourd'hui pour la boutique
    depenses_du_jour = Depense.objects.filter(
        entite='BOUTIQUE',
        date_depense=aujourdhui
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0')

    # 🟢 Montant encore autorisé
    reste_autorise = recette_brute_jour - depenses_du_jour

    if request.method == 'POST':
        form = DepenseForm(request.POST, request.FILES)
        if form.is_valid():
            depense = form.save(commit=False)
            if depense.montant > reste_autorise:
                messages.error(
                    request,
                    f"Montant trop élevé ! Dépense maximum autorisée aujourd'hui : {reste_autorise:.2f} $"
                )
            else:
                depense.entite = 'BOUTIQUE'
                depense.save()
                messages.success(request, "Dépense enregistrée pour la Boutique.")
                return redirect('liste_depenses_boutique')
    else:
        form = DepenseForm()

    return render(request, 'core/depenses/ajouter_boutique.html', {
        'form': form,
        'recette_brute_jour': recette_brute_jour,
        'depenses_du_jour': depenses_du_jour,
        'reste_autorise': reste_autorise,
    })


@login_required
def ajouter_depense_salon(request):
    profil = ProfilUtilisateur.objects.get(user=request.user)
    if profil.role not in ('GESTIONNAIRE_SALON', 'ADMIN'):
        return HttpResponseForbidden()

    today = timezone.localdate()

    # CA brut du jour
    brut_homme = Prestation.objects.filter(
        date_prestation__date=today,
        secteur__nom='HOMME'
    ).aggregate(total=Sum('montant_paye'))['total'] or Decimal('0')
    brut_femme = Prestation.objects.filter(
        date_prestation__date=today,
        secteur__nom='FEMME'
    ).aggregate(total=Sum('montant_paye'))['total'] or Decimal('0')

    # Parts salon
    dispo_homme = brut_homme * Decimal('0.5')
    dispo_femme = brut_femme * Decimal('0.5')

    # Dépenses déjà réalisées
    dep_h = Depense.objects.filter(
        entite='SALON', secteur='HOMME', date_depense=today
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0')
    dep_f = Depense.objects.filter(
        entite='SALON', secteur='FEMME', date_depense=today
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0')

    reste_h = dispo_homme - dep_h
    reste_f = dispo_femme - dep_f

    if request.method=='POST':
        form = DepenseForm(request.POST, request.FILES)
        if form.is_valid():
            dep = form.save(commit=False)
            dep.entite = 'SALON'
            # contrôle selon le secteur choisi
            if dep.secteur == 'HOMME' and dep.montant > reste_h:
                form.add_error('montant',
                    f"Max autorisé pour HOMME aujourd'hui : {reste_h:.2f} CDF")
            elif dep.secteur == 'FEMME' and dep.montant > reste_f:
                form.add_error('montant',
                    f"Max autorisé pour FEMME aujourd'hui : {reste_f:.2f} CDF")
            else:
                dep.save()
                messages.success(request, "Dépense salon enregistrée.")
                return redirect('liste_depenses_salon')
    else:
        form = DepenseForm()

    return render(request, 'core/depenses/ajouter_salon.html', {
        'form': form,
        'brut_homme': brut_homme,
        'dispo_homme': dispo_homme,
        'dep_h': dep_h,
        'reste_h': reste_h,
        'brut_femme': brut_femme,
        'dispo_femme': dispo_femme,
        'dep_f': dep_f,
        'reste_f': reste_f,

    })
