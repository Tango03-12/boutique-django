from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now, timedelta
from django.db.models import Sum, Count
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from .models import *


# ------------- Gestion des Produits ---------------------------------------


#selection et affichage des produits
def liste_produits(request):
    produits = Produit.objects.filter(quantite_stock__gt=0)  # Filtre les produits disponibles
    return render(request, 'boutique/shop.html', {'produits': produits})


#Index et affichage des produits en top 6
def index(request):
    produits = Produit.objects.all()[:6]  # Afficher 6 produits en vedette
    return render(request, 'boutique/index.html', {'produits': produits})


#Selection de tous les produits
def shop(request):
    produits = Produit.objects.filter(quantite_stock__gt=0)
    return render(request, 'boutique/shop.html', {'produits': produits})


#Ajouter un produit à la base de données
def ajouter_produit(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES)  # Gérer l'image
        if form.is_valid():
            form.save()
            return redirect('liste_produits')
    else:
        form = ProduitForm()
    
    return render(request, 'boutique/produits/ajouter_produit.html', {'form': form})


#Supprimer un produit de la base de données
def supprimer_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    produit.delete()
    return redirect('liste_produits')


#rechercher un produit
def rechercher_produit(request):
    query = request.GET.get('q', '')
    produits = Produit.objects.filter(nom__icontains=query, quantite_stock__gt=0) if query else []
    return render(request, 'boutique/recherche/resultats.html', {'produits': produits, 'query': query})

def rechercher_produit(request):
    query = request.GET.get('q', '')
    produits = Produit.objects.filter(nom__icontains=query) if query else Produit.objects.all()
    return render(request, 'boutique/shop.html', {'produits': produits, 'query': query})


#Detail d'un produit
def detail_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    return render(request, 'boutique/produits/details_produit.html', {'produit': produit})


@property
def total(self):
    return self.quantite * self.prix_unitaire


# ------------- Gestion de Panier ---------------------------------------


#Affichage du panier

def cart(request):
    client = None
    client_id = request.session.get('client_id')
    if client_id:
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            client = None

    # Ne montrer le panier que si un client est sélectionné
    panier_détaillé = []
    if client:
        panier = request.session.get("panier", {})  # {'1': 2, '3': 1}
        produits = Produit.objects.filter(id__in=panier.keys())

        for produit in produits:
            quantite = panier.get(str(produit.id), 0)
            total = produit.prix * quantite
            panier_détaillé.append({
                'produit': produit,
                'quantite': quantite,
                'total': total
            })

    if not client:
        request.session["panier"] = {}


    return render(request, "boutique/cart.html", {
        "client": client,
        "panier_détaillé": panier_détaillé
    })






#Ajouter un produit au panier
def ajouter_au_panier(request, produit_id):
    # Vérifie si un client est sélectionné
    if 'client_id' not in request.session:
        messages.error(request, "Veuillez d'abord sélectionner un client.")
        return redirect('ajouter_client')  # ou une autre page adaptée

    panier = request.session.get('panier', {})

    if str(produit_id) in panier:
        panier[str(produit_id)] += 1
    else:
        panier[str(produit_id)] = 1

    request.session['panier'] = panier  # mise à jour de la session
    messages.success(request, "Produit ajouté au panier.")
    # return redirect('cart')  # ou une autre vue
    return redirect('liste_produits')  # ou autre



#Valider la commande
# boutique/views.py


from decimal import Decimal
from django.utils import timezone

def valider_commande(request):
    panier = request.session.get('panier', {})

    if not panier:
        messages.warning(request, "Le panier est vide.")
        return redirect('cart')

    client_id = request.session.get('client_id')
    if not client_id:
        messages.warning(request, "Aucun client sélectionné.")
        return redirect('ajouter_client')

    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        messages.error(request, "Client introuvable.")
        return redirect('ajouter_client')

    produits_commande = []
    total_vente = Decimal('0.00')

    # Vérifier d'abord que tous les produits sont disponibles en quantité suffisante
    for produit_id, quantite in panier.items():
        try:
            produit = Produit.objects.get(id=produit_id)
            quantite = int(quantite)
            if produit.quantite_stock < quantite:
                messages.error(request, f"Stock insuffisant pour le produit {produit.nom}. Stock dispo : {produit.quantite_stock}")
                return redirect('cart')
            produits_commande.append((produit, quantite))
        except Produit.DoesNotExist:
            messages.error(request, f"Produit avec l'ID {produit_id} introuvable.")
            return redirect('cart')

    # Création de la vente après validation
    vente = Vente.objects.create(client=client, date_vente=timezone.now())

    for produit, quantite in produits_commande:
        prix_total = produit.prix * quantite
        total_vente += prix_total

        DetailVente.objects.create(
            vente=vente,
            produit=produit,
            quantite=quantite,
            prix_unitaire=produit.prix
        )

        # Mise à jour du stock
        produit.quantite_stock -= quantite
        produit.save()

    vente.total = total_vente
    vente.save()

    # Vider le panier
    request.session['panier'] = {}
    request.session.modified = True

    messages.success(request, f"Commande validée avec succès. Vente #{vente.id}")
    return redirect('detail_vente', vente_id=vente.id)  


def detail_vente(request, vente_id):
    vente = get_object_or_404(Vente, id=vente_id)
    return render(request, 'boutique/ventes/detail_vente.html', {'vente': vente})


#Supprimer un produit du panier
def retirer_produit(request, produit_id):
    # On récupère le panier depuis la session (convertit les clés en str si nécessaire)
    panier = request.session.get('panier', {})

    # Assurer que produit_id est bien une chaîne car les clés de session sont souvent des strings
    produit_id_str = str(produit_id)

    # Si le produit est dans le panier, on le supprime
    if produit_id_str in panier:
        del panier[produit_id_str]
        request.session['panier'] = panier  # Mise à jour de la session
        request.session.modified = True  # Indique à Django que la session a changé

    return redirect('cart') 


# ------------- Gestion des catégories ---------------------------------------


#Selection et affichage des catégories
def liste_categories(request):
    categories = Categorie.objects.all()
    return render(request, 'boutique/categories/liste_categorie.html', {'categories': categories})


#Ajouter une catégorie
# def ajouter_categorie(request):
#     if request.method == 'POST':
#         nom = request.POST.get('nom')
#         description = request.POST.get('description')

#         if not nom:
#             messages.error(request, "Le nom de la catégorie est requis.")
#         else:
#             Categorie.objects.create(nom=nom, description=description)
#             messages.success(request, "Catégorie ajoutée avec succès.")
#             return redirect('liste_categories')

#     return render(request, 'boutique/categories/ajouter_categorie.html')


#Ajouter une catégorie avec formulaire

def ajouter_categorie(request):
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_categories')
    else:
        form = CategorieForm()

    return render(request, 'boutique/categories/ajouter_categorie.html', {'form': form})

#Supprimer une catégorie
@login_required
def supprimer_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    categorie.delete()
    return redirect('liste_categories')



# ------------- Gestion de Vente ---------------------------------------


#Enregistrer une vente
def ajouter_vente(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    vente = Vente.objects.create(client=client)

    panier = request.session.get('panier', {})
    for produit_id, quantite in panier.items():
        produit = get_object_or_404(Produit, id=produit_id)
        if produit.quantite_stock >= quantite:
            produit.quantite_stock -= quantite
            produit.save()

            DetailVente.objects.create(
                vente=vente,
                produit=produit,
                quantite=quantite,
                prix_unitaire=produit.prix
            )
        else:
            return render(request, 'boutique/cart.html', {'erreur': f"Stock insuffisant pour {produit.nom}"})

    # Calcul du total de la vente
    vente.total = DetailVente.objects.filter(vente=vente).aggregate(
    total=Sum(models.F('prix_unitaire') * models.F('quantite'))
    )['total'] or 0
    vente.save()

    # Suppression du panier après validation
    request.session['panier'] = {}
    return redirect('afficher_facture', vente_id=vente.id)


#Afficher la facture
def afficher_facture(request, vente_id):
    vente = get_object_or_404(Vente, id=vente_id)
    return render(request, 'boutique/ventes/facture.html', {'vente': vente})


# ------------- dashboard ---------------------------------------

#Tableau de bord
def tableau_de_bord(request):
    total_ventes = Vente.objects.aggregate(Sum('total'))['total__sum'] or 0
    derniere_semaine = now() - timedelta(days=7)
    ventes_semaine = Vente.objects.filter(date_vente__gte=derniere_semaine).count()

    produits_plus_vendus = DetailVente.objects.values('produit__id', 'produit__nom') \
        .annotate(total_vendu=Sum('quantite')) \
        .order_by('-total_vendu')[:5]

    produits_rupture = Produit.objects.filter(quantite_stock=0).count()

    paiement_statistiques = Paiement.objects.values('mode_paiement') \
        .annotate(nombre=Count('mode_paiement'))

    return render(request, 'boutique/tableau_de_bord.html', {
        'total_ventes': total_ventes,
        'ventes_semaine': ventes_semaine,
        'produits_plus_vendus': produits_plus_vendus,
        'produits_rupture': produits_rupture,
        'paiement_statistiques': paiement_statistiques
    })



# ------------- Authentification ---------------------------------------


#connexion
def login_view(request):
    if request.method == 'POST':
        telephone = request.POST.get('telephone')
        mot_de_passe = request.POST.get('password')

        if telephone and mot_de_passe:
            user = authenticate(request, username=telephone, password=mot_de_passe)

            if user is not None:
                login(request, user)
                return redirect('index')  # Redirige vers la page d'accueil ou tableau de bord
            else:
                messages.error(request, "Téléphone ou mot de passe incorrect.")
        else:
            messages.warning(request, "Veuillez remplir tous les champs.")
    
    return render(request, 'boutique/auth/login.html')




#déconnexion
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('login_view')  # Redirige vers la page de connexion


#inscription
def register(request):
    if request.method == "POST":
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} ! Votre compte a été créé.")
            return redirect("index")
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = InscriptionForm()

    return render(request, "boutique/auth/register.html", {"form": form})



#Ajouter un client
@login_required
def ajouter_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            request.session['client_id'] = client.id
            messages.success(request, "Client sélectionné avec succès.")
            return redirect('liste_produits')
    else:
        form = ClientForm()
    
    return render(request, 'boutique/clients/ajouter_client.html', {'form': form})



def liste_clients(request):
    clients = Client.objects.all()
    return render(request, "boutique/clients/liste_client.html", {"clients": clients})


def changer_client(request):
    # Supprimer le client courant de la session
    if 'client_id' in request.session:
        del request.session['client_id']
        request.session.modified = True

    # Vider aussi le panier pour éviter les incohérences
    if 'panier' in request.session:
        del request.session['panier']

    # Rediriger vers la page pour choisir/ajouter un nouveau client
    return redirect('ajouter_client')