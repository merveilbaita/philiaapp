from django.urls import path
from .views import inscription_view,connexion_view,deconnexion_view,dashboard_view, liste_depenses, ajouter_depense
from core.views import *

urlpatterns = [
    path('inscription/', inscription_view, name='inscription'),
    path('', connexion_view, name='connexion'),
    path('deconnexion/', deconnexion_view, name='deconnexion'),
    path('dashboard/', dashboard_view, name='dashboard'),
    #path('depenses/', liste_depenses, name='liste_depenses'),
    #path('depenses/ajouter/', ajouter_depense, name='ajouter_depense'),
    path('depenses/boutique/', liste_depenses_boutique, name='liste_depenses_boutique'),
    path('depenses/boutique/ajouter/', ajouter_depense_boutique, name='ajouter_depense_boutique'),
    
    
]
