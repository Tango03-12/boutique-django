from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import *
from django.core.exceptions import ValidationError

# Formulaire pour ajouter/modifier un produit
class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'image', 'categorie', 'prix', 'quantite_stock']
        labels = {
            'nom': 'Nom du produit',
            'image': 'Image du produit',
            'categorie': 'Catégorie',
            'prix': 'Prix (FCFA)',
            'quantite_stock': 'Quantité en stock'
        }
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'prix': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'quantite_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        help_texts = {
            'prix': 'Entrez le prix en FCFA.',
            'quantite_stock': 'Entrez la quantité disponible.',
        }

# Formulaire pour ajouter/modifier une catégorie
class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description']
        labels = {
            'nom': 'Nom de la catégorie',
            'description': 'Description'
        }
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Formulaire pour ajouter/modifier un client
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'email', 'telephone']
        labels = {
            'nom': 'Nom du client',
            'email': 'Email',
            'telephone': 'Téléphone'
        }
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
        }

# Formulaire pour enregistrer une vente
class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = ['client']
        labels = {'client': 'Client'}
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
        }


# Formulaire pour enregistrer un paiement
class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['vente', 'montant', 'mode_paiement']
        labels = {
            'vente': 'Vente associée',
            'montant': 'Montant (FCFA)',
            'mode_paiement': 'Mode de paiement'
        }
        widgets = {
            'vente': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'mode_paiement': forms.Select(attrs={'class': 'form-control'}),
        }


class InscriptionForm(forms.ModelForm):
    password1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmez le mot de passe', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['telephone', 'email']  # ← on utilise 'telephone', pas 'username'

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if not telephone.isdigit():
            raise ValidationError("Le téléphone doit contenir uniquement des chiffres.")
        return telephone

    def clean(self):
        cleaned_data = super().clean()
        pwd1 = cleaned_data.get("password1")
        pwd2 = cleaned_data.get("password2")

        if pwd1 and pwd2 and pwd1 != pwd2:
            raise ValidationError("Les mots de passe ne correspondent pas.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
