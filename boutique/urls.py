# boutique/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Produits
    path('produits/', views.liste_produits, name='liste_produits'),
    path('produits/ajouter/', views.ajouter_produit, name='ajouter_produit'),
    path('produits/modifier/<int:pk>/', views.modifier_produit, name='modifier_produit'),
    path('produits/supprimer/<int:pk>/', views.supprimer_produit, name='supprimer_produit'),

    # Mouvements de stock
    path('stock/mouvements/', views.historique_mouvements, name='historique_mouvements'),
    path('stock/ajuster/', views.ajouter_mouvement_stock, name='ajouter_mouvement_stock'),

    # Ventes
    path('ventes/', views.liste_ventes, name='liste_ventes'),
    path('ventes/<int:pk>/', views.detail_vente, name='detail_vente'),
    path('ventes/nouvelle/', views.creer_vente, name='creer_vente'),
    path('ventes/journalier/', views.ventes_journaliere, name='ventes_journaliere'),
    path('produit-autocomplete/', views.produit_autocomplete, name='produit_autocomplete'),
]