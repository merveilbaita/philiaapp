from django.urls import path
from . import views
from core.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('dashboard_sal/', views.dashboard_salon, name='dashboard_salon'),
    path('personnel/', views.liste_personnel, name='liste_personnel'),
    path('personnel/ajouter/', views.ajouter_personnel, name='ajouter_personnel'),
    path('personnel/modifier/<int:pk>/', views.modifier_personnel, name='modifier_personnel'),
    path('personnel/supprimer/<int:pk>/', views.supprimer_personnel, name='supprimer_personnel'),
    path('prestations/', views.liste_prestations, name='liste_prestations'),
    path('prestations/ajouter/', views.ajouter_prestation, name='ajouter_prestation'),
    path('commissions/', views.liste_commissions, name='liste_commissions'),
    path('rapports/', views.rapport_salon, name='rapport_salon'),
    # Salon
    path('depenses/salon/', liste_depenses_salon, name='liste_depenses_salon'),
    path('depenses/salon/ajouter/', ajouter_depense_salon, name='ajouter_depense_salon'),
    path('logout/', auth_views.LogoutView.as_view(next_page='connexion'), name='logout'),
     path(
        'rapports/commissions-mensuelles/',
        views.rapport_commissions_mensuelles,
        name='rapport_commissions_mensuelles'
    ),
    path(
        'rapports/depenses-mensuelles/',
        views.rapport_depenses_mensuelles,
        name='rapport_depenses_mensuelles'
    ),
    
]
