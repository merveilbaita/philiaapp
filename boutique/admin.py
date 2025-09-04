from django.contrib import admin

from boutique.models import Produit,Categorie,Vente,MouvementStock,LigneDeVente

# Register your models here.
admin.site.register(Produit)
admin.site.register(Categorie)
admin.site.register(Vente)
admin.site.register(LigneDeVente)
admin.site.register(MouvementStock)