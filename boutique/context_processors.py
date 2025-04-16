# boutique/context_processors.py

def panier_context(request):
    panier = request.session.get('panier', {})
    return {'panier': panier}
