from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import Produit, MouvementStock, Vente, Categorie,LigneDeVente
from .forms import ProduitForm, MouvementStockForm, VenteForm, LigneDeVenteFormSet
from decimal import Decimal
from django.db.models import ExpressionWrapper, F, Sum, DecimalField

# ✅ PRODUIT VIEWS

@login_required
def liste_produits(request):
    """Affiche la liste de tous les produits avec indication de stock bas"""
    produits = Produit.objects.all().select_related('categorie')
    
    # Identifier les produits avec stock bas pour mise en évidence
    produits_stock_bas = [p.id for p in produits if p.est_stock_bas()]
    
    return render(request, 'boutique/produits/liste.html', {
        'produits': produits,
        'produits_stock_bas': produits_stock_bas
    })

@login_required
def ajouter_produit(request):
    """Ajoute un nouveau produit"""
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            produit = form.save()
            messages.success(request, f"Le produit '{produit.nom}' a été ajouté avec succès.")
            return redirect('liste_produits')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ProduitForm()

    return render(request, 'boutique/produits/formulaire.html', {'form': form})

@login_required
def modifier_produit(request, pk):
    """Modifie un produit existant"""
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            produit = form.save()
            messages.success(request, f"Le produit '{produit.nom}' a été modifié avec succès.")
            return redirect('liste_produits')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ProduitForm(instance=produit)
    
    return render(request, 'boutique/produits/formulaire.html', {'form': form})

@login_required
def supprimer_produit(request, pk):
    """Supprime un produit après confirmation"""
    produit = get_object_or_404(Produit, pk=pk)
    
    if request.method == 'POST':
        nom = produit.nom
        produit.delete()
        messages.success(request, f"Le produit '{nom}' a été supprimé.")
        return redirect('liste_produits')
    
    return render(request, 'boutique/produits/confirmer_suppression.html', {'produit': produit})

@login_required
def detail_produit(request, pk):
    """Affiche les détails d'un produit avec son historique de mouvements"""
    produit = get_object_or_404(Produit, pk=pk)
    mouvements = produit.mouvements.all().order_by('-date_mouvement')[:10]  # 10 derniers mouvements
    
    return render(request, 'boutique/produits/detail.html', {
        'produit': produit,
        'mouvements': mouvements
    })

# ✅ STOCK VIEWS

@login_required
def ajouter_mouvement_stock(request):
    """Ajoute un mouvement de stock manuel"""
    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            produit = form.cleaned_data['produit']
            type_mouvement = form.cleaned_data['type_mouvement']
            quantite = form.cleaned_data['quantite']
            raison = form.cleaned_data['raison']
            
            try:
                # Utiliser la méthode ajuster_stock du modèle Produit
                produit.ajuster_stock(
                    quantite=quantite,
                    type_mouvement=type_mouvement,
                    utilisateur=request.user,
                    raison=raison
                )
                messages.success(request, f"Stock de '{produit.nom}' ajusté avec succès.")
                return redirect('historique_mouvements')
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = MouvementStockForm()
    
    return render(request, 'boutique/mouvements/formulaire.html', {'form': form})

@login_required
def historique_mouvements(request):
    """Affiche l'historique des mouvements de stock"""
    mouvements = MouvementStock.objects.select_related('produit', 'utilisateur').order_by('-date_mouvement')
    
    # Filtrage par produit si spécifié
    produit_id = request.GET.get('produit')
    if produit_id:
        mouvements = mouvements.filter(produit_id=produit_id)
    
    return render(request, 'boutique/mouvements/historique.html', {
        'mouvements': mouvements,
        'produits': Produit.objects.all()  # Pour le filtre
    })

# ✅ VENTE VIEWS



# ✅ RAPPORTS VIEWS

@login_required
def rapport_stock(request):
    """Affiche un rapport sur l'état des stocks"""
    produits = Produit.objects.all().select_related('categorie')
    
    # Filtrer par catégorie si spécifié
    categorie_id = request.GET.get('categorie')
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)
    
    # Filtrer par état de stock
    stock_filter = request.GET.get('stock')
    if stock_filter == 'bas':
        produits = [p for p in produits if p.est_stock_bas()]
    elif stock_filter == 'zero':
        produits = produits.filter(quantite_stock=0)
    
    return render(request, 'boutique/rapports/stock.html', {
        'produits': produits,
        'categories': Categorie.objects.all()
    })

@login_required
def rapport_ventes(request):
    """Affiche un rapport sur les ventes"""
    # Implémentation à venir
    return render(request, 'boutique/rapports/ventes.html')


# nouvlle methode de vente

@login_required
def creer_vente(request):
    if request.method == 'POST':
        vente_form = VenteForm(request.POST)
        formset = LigneDeVenteFormSet(request.POST)

        if vente_form.is_valid() and formset.is_valid():
            vente = vente_form.save(commit=False)
            vente.vendeur = request.user
            vente.save()

            lignes = formset.save(commit=False)
            for ligne in lignes:
                ligne.vente = vente
                # 🟢 On vérifie et complète si nécessaire
                if not ligne.prix_unitaire_vente or ligne.prix_unitaire_vente == 0:
                    ligne.prix_unitaire_vente = ligne.produit.prix_vente
                ligne.save()

            vente.calculer_total()
            vente.finaliser()
            messages.success(request, "Vente enregistrée avec succès.")
            return redirect('detail_vente', vente.id)
    else:
        vente_form = VenteForm()
        formset = LigneDeVenteFormSet()

    return render(request, 'boutique/ventes/creer_vente.html', {
        'vente_form': vente_form,
        'formset': formset
    })



@login_required
def detail_vente(request, pk):
    vente = get_object_or_404(Vente, pk=pk)
    lignes = vente.lignes.select_related('produit')  # Optimisation

    return render(request, 'boutique/ventes/detail_vente.html', {
        'vente': vente,
        'lignes': lignes
    })

@login_required
def liste_ventes(request):
    ventes = Vente.objects.select_related('vendeur').order_by('-date_vente')
    return render(request, 'boutique/ventes/liste_ventes.html', {'ventes': ventes})


@login_required
def ventes_journaliere(request):
    # 🔍 Récupérer la date filtrée depuis la requête GET sinon aujourd'hui
    date_str = request.GET.get('date')
    if date_str:
        try:
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date = timezone.now().date()
    else:
        date = timezone.now().date()

    ventes = Vente.objects.filter(date_vente__date=date, est_complete=True)

    lignes = LigneDeVente.objects.filter(vente__in=ventes)

    ca_total = lignes.aggregate(
        total_ca=Sum(ExpressionWrapper(F('prix_unitaire_vente') * F('quantite'), output_field=DecimalField()))
    )['total_ca'] or 0

    cout_total = lignes.aggregate(
        total_cout=Sum(ExpressionWrapper(F('produit__prix_achat') * F('quantite'), output_field=DecimalField()))
    )['total_cout'] or 0

    marge = ca_total - cout_total

    context = {
        'ventes': ventes,
        'ca_total': ca_total,
        'cout_total': cout_total,
        'marge': marge,
        'date': date,
    }
    return render(request, 'boutique/ventes/ventes_journaliere.html', context)