from django.db import models
from django.contrib.auth.models import AbstractUser


class Gerant(AbstractUser):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return self.telephone


# Catégorie de produits
class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

# Produit
class Produit(models.Model):
    nom = models.CharField(max_length=200)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name="produits")
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_stock = models.PositiveIntegerField()
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

# Client
class Client(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    telephone = models.CharField(max_length=20, unique=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

# Vente
class Vente(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    date_vente = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Vente {self.id} - {self.date_vente}"

# Détails de Vente
class DetailVente(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name="details")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"

# Facture
class Facture(models.Model):
    vente = models.OneToOneField(Vente, on_delete=models.CASCADE)
    date_facture = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Facture {self.id} - {self.vente.date_vente}"

# Paiement (TMoney & Flooz)
class Paiement(models.Model):
    MODES_PAIEMENT = [
        ('TMoney', 'TMoney'),
        ('Flooz', 'Flooz'),
        ('Cash', 'Cash')
    ]
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name="paiements")
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=10, choices=MODES_PAIEMENT)
    date_paiement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mode_paiement} - {self.montant} FCFA"
