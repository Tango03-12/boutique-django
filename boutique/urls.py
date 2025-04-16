from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [

    #Route vers la page d'accueil
    path('', views.index, name='index'),

    #Route vers la page de la boutique
    path('shop/', views.shop, name='shop'),

    #Route vers la page du panier
    path('cart/', views.cart, name='cart'),

 #----------------------------- Gestion des produits------------------------------------------

    # Recherche de produits
    path('recherche/', views.rechercher_produit, name='rechercher_produit'),

    #Route pour afficher le détail d'un produit
    path('produit/<int:produit_id>/', views.detail_produit, name='detail_produit'),

    #Route pour afficher la liste des produits
    path('produits/', views.liste_produits, name='liste_produits'),

    #Route pour ajouter un produit
    path('produits/ajouter/', views.ajouter_produit, name='ajouter_produit'),

    #Route pour supprimer un produit
    path('produits/supprimer/<int:produit_id>/', views.supprimer_produit, name='supprimer_produit'),


 #------------------------ Gestion du panier ---------------------------------------------


    #Route pour ajouter un produit au panier
    path('cart/ajouter/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),

    #Route pour enregistrer une vente
    path('cart/vente/ajouter/<int:produit_id>/', views.ajouter_vente, name='ajouter_vente'),

    #Route pour retirer un produit du panier
    path('cart/retirer/<int:produit_id>/', views.retirer_produit, name='retirer_produit'),
    
    path('panier/valider/', views.valider_commande, name='valider_commande'),

    path('vente/<int:vente_id>/', views.detail_vente, name='detail_vente'),


 #------------------------ Gestion des catégories---------------------------------------------

    #Route pour afficher la liste des catégories
    path('categories/', views.liste_categories, name='liste_categories'),

    #Route pour ajouter une catégorie
    path('categories/ajouter/', views.ajouter_categorie, name='ajouter_categorie'),

    #Route pour supprimer une catégorie
    path('categories/supprimer/<int:categorie_id>/', views.supprimer_categorie, name='supprimer_categorie'),


 # -------------------- Authentification ---------------------

    #Route vers l'inscription
    path('auth/register/', views.register, name='register'),

    #Route vers la connexion
    path('auth/login/', views.login_view, name='login_view'),

    #Route vers la deconnection
    path('logout/', views.logout_view, name='logout_view'),



    # -------------------- Tableau de bord ----------------------

    #Route vers le Tableau de bord
    path('dashboard/', views.tableau_de_bord, name='tableau_de_bord'),


    # clients
    path('client/', views.liste_clients, name='liste_clients'),
    
    path('client/ajouter/', views.ajouter_client, name='ajouter_client'),

    path('client/changer/', views.changer_client, name='changer_client'),


    


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)