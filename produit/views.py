from .models import*
from django.shortcuts import get_object_or_404
from rest_framework import status
from .serializer import*
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView,DestroyAPIView,GenericAPIView,ListAPIView
from rest_framework.response import Response
from rest_framework import authentication, permissions,generics
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.mixins import ListModelMixin
from rest_framework import filters
from rest_framework.permissions import  BasePermission, SAFE_METHODS
from user.serializer import UserSerializer 
from user.models import User
import json
from rest_framework.parsers import JSONParser
import decimal
from rest_framework.pagination import PageNumberPagination
from user.notifications import NotificationCommandeAuVendeur,NotificationNewProductToFollower 
 
  
 

class MyPaginationClass(PageNumberPagination):
    page_size = 4 
    page_size_query_param = 'page_size'
    
 
class VendeurPermission(BasePermission):
	message = 'La modification ou suppression d un produit ne peut etre fait que par le vendeur'

	def has_object_permission(self, request, view, obj):
		if request.method in SAFE_METHODS:
			return True
		return obj.vendeur == request.user



#Gestion recherche a revoir
class ProduitSearch(generics.ListAPIView):
	permission_classes = [permissions.AllowAny]
	queryset = Produit.objects.filter(active=True,recycler=False,desactiver=False)
	serializer_class = ProductSerializer
	filter_backends = [filters.SearchFilter]
	search_fields = search_fields = ['^nom','^description','^category__category']

#list des categories
class CategoryList(ListAPIView):
	permission_classes = [permissions.AllowAny]
	def get(self,request):
		category=Category.objects.all().order_by('-id')
		serializer=CategorySerializer(category,many=True)
		return Response(serializer.data)


#liste des regions
class RegionList(ListAPIView):
	queryset = Region.objects.all().order_by('-id')
	serializer_class = RegionSerializer
	permission_classes = [permissions.AllowAny]


#liste des adresses de livraison
class AdressList(ListAPIView):
	serializer_class=AdresseSerializer
	queryset=Adress.objects.filter(bureau=False).order_by('-id')
	permission_classes = [permissions.AllowAny]

#Pour l ajout de produit
class GetdeviseLocationCategorie(APIView):
	#permission_classes = [permissions.AllowAny]
	def get(self,request):
		devise=Devise.objects.all().order_by('-id')
		deviseserializer=DeviseSerializer(devise,many=True)
		location=Region.objects.all().order_by('-id')
		locationserializer=RegionSerializer(location,many=True)   #Pays Ensuite region
		categorie=Category.objects.all().order_by('-id')
		catserializer=CategorySerializer(categorie,many=True)
		return Response({'devise':deviseserializer.data,'location':locationserializer.data,
			'category':catserializer.data})
		

#ajout de produit au panier
class AddCartView(APIView):   
	def post(self,request,*args,**kwargs):
		slug=request.data.get('slug')
		if slug is None:
			return Response({'error':'id invalide'})
		else:
			produit=Produit.objects.get(slug=slug,recycler=False,desactiver=False,active=True)
			cart=Cart.objects.get(proprietaire=request.user)
			if produit.variation==False:
				produit_cart=cart.cartproduct.filter(product=produit)
				if produit_cart.exists():
					cart_product=produit_cart.last()
					if produit.qte>cart_product.quantity:
						cart_product.quantity+=1
						cart_product.subtotal+=produit.prix
						cart_product.save()
						cart.total+=produit.prix
						cart.save()
						return Response({'message':'produit existant reajoute fois'})
				else:
					cart_product=CartProduct.objects.create(product=produit,quantity=1,
					 subtotal=produit.prix,client=request.user)
					cart.cartproduct.add(cart_product)
					cart.total+=produit.prix
					cart.save()
					return Response({'message':'premiere fois'})

			else:
				produitimg_id=request.data.get('prodimg')
				prodimg=ProduitImage.objects.get(id=produitimg_id,active=True,desactiver=False,recycler=False)
				produitimg_cart=cart.cartproduct.filter(imageproduct=prodimg,)
				if produitimg_cart.exists():
					cart_produitimg=produitimg_cart.last()
					if prodimg.quantite>cart_produitimg.quantity:
						cart_produitimg.quantity+=1
						cart_produitimg.subtotal+=produit.prix
						cart_produitimg.save()
						return Response({'message':'premiere fois'})
				else:
					cart_produitimg=CartProduct.objects.create(imageproduct=prodimg , quantity=1,
					 subtotal=produit.prix,client=request.user,product=produit)
					cart.cartproduct.add(cart_produitimg)
					cart.total+=produit.prix
					cart.save()
					return Response({'message':'cart cree produit ajoute '})

#panier d un utilisateur	
class CartView(RetrieveAPIView):
	serializer_class=CartSerializer
	def get_object(self):
		try:
			cart=Cart.objects.filter(proprietaire=self.request.user,ordered=False).first()
			return cart
		except ObjectsDoesNotExist:
			return Response({'message':'cart non existant'})


#Produit Une category donnee
class ProduitCategory(generics.ListAPIView):
	permission_classes = [permissions.AllowAny]
	pagination_class =MyPaginationClass
	#queryset=Produit.objects.all()
	serializer_class=ProductSerializer

	def get_queryset(self, *args, **kwargs):
		id=self.kwargs['pk']
		cat=Category.objects.get(id=id)
		produit=Produit.objects.filter(category=cat,active=True,recycler=False,desactiver=False).order_by('-id')
		return produit

#Produit boutique pour visiteur 
class ProduitBoutique(generics.ListAPIView):
	permission_classes = [permissions.AllowAny]
	pagination_class =MyPaginationClass
	#queryset=Produit.objects.all()
	serializer_class=ProductSerializer

	def get_queryset(self, *args, **kwargs):
		id=self.kwargs['pk']
		boutique=Boutique.objects.get(id=id)
		user=boutique.user
		produit=Produit.objects.filter(vendeur=user,recycler=False,desactiver=False).order_by('-id')
		return produit

#Produit boutique pour le vendeur lui meme
class ProduitBoutiqueVendeur(generics.ListAPIView):
	pagination_class =MyPaginationClass
	#queryset=Produit.objects.all()
	serializer_class=ProductSerializer

	def get_queryset(self, *args, **kwargs):
		user=self.request.user
		produit=Produit.objects.filter(vendeur=user,recycler=False,desactiver=False).order_by('-id')
		return produit


#Profil boutique vu client	
class BoutiqueVuClient(APIView):
	permission_classes = [permissions.AllowAny]
	def post(self,request):
		data=request.data 
		id=data['id']
		boutique=Boutique.objects.get(id=id)
		serializer=BoutiqueSerializer(boutique)
		isabonned=False
		if request.user.is_authenticated:
			user=request.user
			userfollower=Follower.objects.get(user=user)
			for follower in boutique.follower.all():
				if follower.id==userfollower.id:
					isabonned=True
			return Response({'boutique':serializer.data,'isabonned':isabonned,'islog':True})
		else:
			return Response({'boutique':serializer.data,'isabonned':isabonned,'islog':False})

#Suivi d une boutique par un utilisateur
class AddFollower(APIView):
	def post(self,request):
		data=request.data
		id_boutique=data['id_boutique']
		boutique=Boutique.objects.get(id=id_boutique)
		follower,created=Follower.objects.get_or_create(user=request.user)
		boutique.follower.add(follower)
		boutique.nbrefollower+=1
		boutique.save()
		return Response({'message':'nouveau follower'})

#unfollow boutique par un utilisateur
class RemoveFollower(ModelViewSet):
	queryset=Boutique.objects.all()
	serializer_class=BoutiqueSerializer
	@action(methods=["delete"], detail=False, url_path='removefollower/(?P<pk>\d+)')
	def remove_follower(self,request,*args,**kwargs):
		id_boutique=self.kwargs['pk']
		boutique=Boutique.objects.get(id=id_boutique)
		follower=Follower.objects.get(user=self.request.user)
		boutique.follower.remove(follower)
		boutique.nbrefollower-=1
		boutique.save()
		return Response({'message':'follower supprime'})

#Profil boutique	
class ProfileVendeur(APIView):
	permission_classes = [permissions.AllowAny]
	def post(self,request):
		slug=request.data.get('slug')
		produit=Produit.objects.get(slug=slug)
		user=produit.vendeur
		boutique=Boutique.objects.get(user=user)
		serializer=BoutiqueSerializer(boutique)
		return Response(serializer.data)

#Boutique par le vendeur lui meme
class BoutiqueView(APIView):
	def get(self,request):
		boutique=Boutique.objects.get(user=request.user)
		if boutique is not None:
			serializer=BoutiqueSerializer(boutique)
			return Response(serializer.data)



#Operation sur le panier
class CartProductDeleteSingle(ModelViewSet):
	serializer_class=CartSerializer
	queryset=Cart.objects.all() 

	@action(methods=["put"], detail=False, url_path='mycart/remove/(?P<pk>\d+)')
	def product_remove_from_cart(self, *args, **kwargs):
		cart = Cart.objects.get(proprietaire=self.request.user)
		id=self.kwargs['pk']
		if id is None:
			return Response({'error':'id invalide'})
		else:
			cartproduct = CartProduct.objects.get(id=id)
			cartproduct.quantity-=1
			if cartproduct.product is None:
				cartproduct.subtotal-=cartproduct.imageproduct.produit.prix
				cartproduct.save()
				cart.total-=cartproduct.imageproduct.produit.prix
				cart.save()
			else:
				cartproduct.subtotal-=cartproduct.product.prix
				cartproduct.save()
				cart.total-=cartproduct.product.prix
				cart.save()
			if cartproduct.quantity==0:
				cart.cartproduct.remove(cartproduct)
				cartproduct.delete()
				cart.save()
			return Response({"message":'produit supprime'})

	@action(methods=["put"], detail=False, url_path='mycart/removesingle/(?P<pk>\d+)')
	def product_remove_all_cartproduct(self, *args, **kwargs):
		cart = Cart.objects.get(proprietaire=self.request.user)
		id=self.kwargs['pk']
		if id is None:
			return Response({'error':'id invalide'})
		else:
			cartprod = CartProduct.objects.get(id=id)
			cart.cartproduct.remove(cartprod)
			cartprod.delete()
			cart.total-=cartprod.subtotal
			cart.save()
			return Response({"message":'produit supprime'})

	@action(methods=["put"], detail=False, url_path='mycart/removeall')
	def remove_all(self,request):
		cart = Cart.objects.get(proprietaire=request.user)
		cart.cartproduct.all().delete()
		cart.total=0
		cart.save()
		return Response({'message':'carte videe'})

#Ajout Produit
class AjoutDetailProduit(APIView):
	parser_classes = (MultiPartParser, FormParser)
	def post(self,request):
		boutique=Boutique.objects.get(user=request.user)
		if boutique.active==True:
			data=request.data
			cat_id=request.data.get('cat_id')
			category=Category.objects.get(id=cat_id)
			region_id=request.data.get('region_id')
			region=Region.objects.get(id=region_id)
			devise_id=request.data.get('devise_id')
			devise=Devise.objects.get(id=devise_id)
			serializer=ProductSerializer(data=data)
			if serializer.is_valid():
				serializer.save(category=category,region=region,devise=devise,boutique=boutique,
					vendeur=request.user,active=False,recycler=False,desactiver=False)
			#return Response({'success':'produit load'})
			return Response(serializer.data)

#Ajout des images produits
class AjoutImageProduit(APIView):
	def post(self,request):
		data=request.data
		id=data['id']
		produit=Produit.objects.get(id=id)
		serializer=ProduitImageserializer(data=data)
		if serializer.is_valid():
			serializer.save(produit=produit,active=True,recycler=False,desactiver=False)
			produit.active=True
			produit.save()
			return Response({'success':'imgadd'})
		#return Response(serializer.errors)

class NotifyToFollower(APIView):
	def post(self,request):
		data=request.data
		id=data['id']
		produit=Produit.objects.get(id=id,recycler=False,active=True)
		if request.user==produit.vendeur:
			NotificationNewProductToFollower(produit) 
			return Response({'success':'notify'})


#Produit pour la modification
class GetProduitAndImages(APIView):
	def post(self,request):
		slug=request.data.get('slug')
		produit=Produit.objects.get(slug=slug)
		if request.user==produit.vendeur:
			produitimg=ProduitImage.objects.filter(produit=produit,active=True,recycler=False,
				desactiver=False).order_by('-id')
			produitserializer=ProductSerializer(produit)
			imgserializer=ProduitImageserializer(produitimg,many=True)
			return Response({'produit':produitserializer.data,'image':imgserializer.data})


#### Gestion de la modification d un produit
class Manageproduit(ModelViewSet):
	queryset=Produit.objects.all()
	serializer_class=ProductSerializer 
	#permission_classes=[permissions.AllowAny]
	
	@action(methods=["put"], detail=False, url_path='supprimer/(?P<slug>[\w-]+)')
	def sup_prod(self,request,*args,**kwargs):
		slug=self.kwargs['slug']
		produit=Produit.objects.get(slug=slug,)
		if request.user==produit.vendeur:
			produit.active=False
			produit.recycler=True
			produit.save()
			allproduitimg=ProduitImage.objects.filter(produit=produit)
			for im in allproduitimg:
				im.active=False
				im.recycler=True
				im.save()
				return Response({'message':'produit supprime'})

	@action(methods=["put"], detail=False, url_path='modifproduit/(?P<slug>[\w-]+)')
	def modif_produit(self,request,*args,**kwargs):
		slug=self.kwargs['slug']
		prod=Produit.objects.get(slug=slug)
		if prod.vendeur==request.user:
			data=request.data
			cat_id=data['cat_id']
			region_id=data['region_id']
			devise_id=data['devise_id']
			devise=Devise.objects.get(id=devise_id)
			category=Category.objects.get(id=cat_id)
			region=Region.objects.get(id=region_id)
			serializer=ProductSerializer(prod,data=data)
			variation=data['variation']
			prix=decimal.Decimal(data['prix'])
			if serializer.is_valid():
				cartproduct=CartProduct.objects.filter(product=prod)
				for cart in cartproduct:
					cart.subtotal=cart.quantity*prix
					cart.save()
					#print(cart.subtotal)
				serializer.save(devise=devise,category=category,region=region,active=True,recycler=False)
				return Response({'message':"Produit bien modifie"})
			return Response(serializer.errors)
			#return Response(serializer.errors)

	@action(methods=["put"], detail=False, url_path='modifimageproduit/(?P<pk>\d+)')
	def modif_imageproduit(self,request,*args,**kwargs):
		id=self.kwargs['pk']
		produitimg=ProduitImage.objects.get(id=id)
		if produitimg.produit.vendeur==request.user:
			data=request.data
			serializer=ProduitImageserializer(produitimg,data=data)
			if serializer.is_valid():
				serializer.save(active=True)
				return Response({'success':'modification image produit'})

	@action(methods=["put"], detail=False, url_path='modificationdetailimgproduit/(?P<pk>\d+)')
	def modif_detailimg(self,request,*args,**kwargs):
		id=self.kwargs['pk']
		produitimg=ProduitImage.objects.get(id=id)
		if produitimg.produit.vendeur==request.user:
			data=request.data
			quantite=int(data['quantite'])
			if quantite>0:
				serializer=ProduitImageserializer(produitimg,data=data)
				if serializer.is_valid():
					serializer.save(active=True)
					return Response({'success':'modification image produit'})
			

	@action(methods=["put"], detail=False, url_path='suppression/(?P<pk>\d+)')
	def sup_prodimg(self,request,*args,**kwargs):
		id=self.kwargs['pk']
		produitimg=ProduitImage.objects.get(id=id)
		produit=produitimg.produit
		allproduitimg=ProduitImage.objects.filter(produit=produit,active=True,recycler=False)
		count=allproduitimg.count()
		#print(count)
		#if request.user==produitimg.produit.vendeur:
		if produit.variation==True:
			if count>2:
				produitimg.active=False
				produitimg.recycler=True
				produitimg.save()
				produit.thumbnail=allproduitimg[0].image
				produit.save()
				return Response({'message':'produitimg recycler'})
		else:
			if count>1:
				produitimg.active=False
				produitimg.recycler=True
				produitimg.save()
				produit.thumbnail=allproduitimg[0].image
				produit.save()
				return Response({'message':'produitimg recycler'})



class ReactivationProduit(APIView):
	def post(self,request):
		data=request.data
		id=data['id'] 
		produit=Produit.objects.get(id=id)
		if request.user==produit.vendeur:
			produit.active=True
			produit.vendu=True
			produit.save()
			return Response({'message':'reactivation reussie'})

#recuperer le panier de commande
class GetPanier(generics.ListAPIView):
	pagination_class =MyPaginationClass
	serializer_class=CartProductSerializer
	#permission_classes = [permissions.AllowAny]

	def get_queryset(self, *args, **kwargs):
		cart=Cart.objects.get(proprietaire =self.request.user)
		cartprod=cart.cartproduct.all().order_by('-id')
		return cartprod
		

		
#Gestion commande
class PostCommande(APIView):
	def post(self,request):
		data=request.data
		produitcommande=CartProduct.objects.get(id=data['cart_id'])
		if produitcommande.product.variation==True:
			if produitcommande.imageproduct.active==True and  produitcommande.imageproduct.desactiver==False and produitcommande.imageproduct.recycler==False  and produitcommande.imageproduct.quantite>=produitcommande.quantity:
				adress_id=data['adress_id']
				vendeur=produitcommande.imageproduct.produit.vendeur
				prod=produitcommande.imageproduct.produit.nom
				adress=Adress.objects.get(id=adress_id)
				serializer=CommandeSerializer(data=data)
				user=request.user
				livraison=round(decimal.Decimal(data['livraison']),2)
				commission=round((2*produitcommande.imageproduct.produit.prix*produitcommande.quantity)/decimal.Decimal(100),2)
				montant_vendeur=produitcommande.quantity*produitcommande.imageproduct.produit.prix-commission
				if serializer.is_valid():
					serializer.save(produitcommande=produitcommande,
						adress=adress,active=False,livraison=livraison,acheteur=user,
						statut_commande='produit en attente de livraison',commission=commission,
						montant_vendeur=montant_vendeur,payer=False)
					id_commande=serializer.data['id']
					return Response({'id':id_commande})
					#return Response(serializer.errors)
		else:
			if produitcommande.product.active==True and produitcommande.product.desactiver==False and produitcommande.product.recycler==False and produitcommande.product.qte>=produitcommande.quantity:
				adress_id=data['adress_id']
				vendeur=produitcommande.product.vendeur
				prod=produitcommande.product.nom
				adress=Adress.objects.get(id=adress_id)
				serializer=CommandeSerializer(data=data)
				user=request.user
				livraison=decimal.Decimal(data['livraison'])
				commission=round((2*produitcommande.product.prix*produitcommande.quantity)/decimal.Decimal(100),2)
				montant_vendeur=produitcommande.quantity*produitcommande.product.prix-commission
				if serializer.is_valid():
					serializer.save(produitcommande=produitcommande,
						adress=adress,active=False,livraison=livraison,acheteur=user,
						statut_commande='produit en attente de livraison',commission=commission,
						montant_vendeur=montant_vendeur,payer=False)
					id_commande=serializer.data['id']
					return Response({'id':id_commande})
					#return Response(serializer.errors)
				


class CommandePay(APIView):
	def post(self,request):
		id=request.data.get('id')
		command=Commande.objects.get(id=id,payer=False,acheteur=request.user)
		serializer=CommandeSerializer(command)
		return Response(serializer.data)

class ConfirmationPayCommande(APIView):
	def post(self,request):
		id=request.data.get('id')
		command=Commande.objects.get(id=id,acheteur=request.user,active=False)
		if command.produitcommande.product.variation==True:
			command.produitcommande.imageproduct.quantite-=1
			command.produitcommande.imageproduct.save()
			vendeur=command.produitcommande.product.vendeur
			if command.produitcommande.imageproduct.quantite==0:
				command.produitcommande.imageproduct.active=False
				command.produitcommande.imageproduct.save()
				prod=command.produitcommande.product
				allproduitimg=ProduitImage.objects.filter(produit=prod)
				tousnull=all(im.quantite==0 for im in allproduitimg)
				if tousnull:
					prod.active=False
					prod.save()
			command.payer=True
			command.active=True
			command.statut_commande="produit en attente de livraison "
			command.save()
			NotificationCommandeAuVendeur(command)
			return Response({'commandepay':'success'})
		else:
			command.produitcommande.product.qte-=1
			command.produitcommande.product.save()
			if command.produitcommande.product.qte==0:
				command.produitcommande.product.active=False
				command.produitcommande.product.save()
			vendeur=command.produitcommande.product.vendeur
			command.payer=True
			command.active=True
			command.statut_commande="produit en attente de livraison "
			command.save()
			NotificationCommandeAuVendeur(command)
			return Response({'commandepay':'success'})

class AnnulationCommande(ModelViewSet):
	queryset=Commande.objects.all()
	serializer_class=CommandeSerializer 

	@action(methods=["put"], detail=False, url_path='suppressioncommandeuser')
	def supprim(self,request,*args,**kwargs):
		id=self.request.data.get('id')
		command=Commande.objects.get(id=id)
		if command is not None:
			command.delete()
			return Response({'suppression ':'success'})

#Recu commande			
class GetCommande(APIView):
	def post(self,request):
		data=request.data
		id=data['id']
		commande=Commande.objects.get(id=id,payer=True,active=True,acheteur=request.user)
		serializer=CommandeSerializer(commande)
		return Response(serializer.data)

class GetCommandeDetail(APIView):
	def post(self,request):
		data=request.data
		id=data['id']
		commande=Commande.objects.get(id=id,acheteur=request.user)
		serializer=CommandeSerializer(commande)
		return Response(serializer.data)
		

class NotificationDetail(APIView):
	def post(self,request):
		data=request.data
		id=data['id']
		notify=Notification.objects.get(id=id,active=True)
		if notify.user==request.user:
			serializer=NotificationSerializer(notify)
			return Response(serializer.data)
						

class ActivationCommande(APIView):
	def post(self,request):
		id=request.data.get('pid')
		commande=Commande.objects.get(id=id)
		commande.active=True
		commande.save()
		commande.statut_commande="produit en attente de livraison"
		commande.save()
		return Response({'message':'commande prise en charge '})

		

class RemoveCommande(ModelViewSet):
	queryset=Commande.objects.all()
	serializer_class=CommandeSerializer

	@action(methods=["delete"], detail=False, url_path='supprimer/(?P<pk>\d+)')
	def noter(self,request,*args,**kwargs):
		id=self.kwargs['pk']
		commande=Commande.objects.get(id=id)
		commande.delete()
		return Response({'message':'commande non prise en charge'})
		

#Detail produit 
class GetDetailProduit(APIView):
	permission_classes = [permissions.AllowAny]
	def post(self,request):
		data=request.data
		slug=data['slug']
		produit=Produit.objects.get(slug=slug)
		produitserializer=ProductSerializer(produit)
		produitimg=ProduitImage.objects.filter(produit=produit).order_by('-id')
		serializer=ProduitImageserializer(produitimg,many=True)
		return Response({'produitimage':serializer.data,'produit':produitserializer.data})

		
#Changement logo boutique
class EditBoutiquePic(APIView):
	parser_classes = [MultiPartParser, FormParser]
	def post(self,request,format=None):
		boutique=Boutique.objects.get(user=request.user)
		data=request.data
		serializer=BoutiqueSerializer(boutique,data=data)
		if serializer.is_valid():
			serializer.save()
			return Response({'success':'load image'})
		return Response(serializer.errors)

#Changement desription boutique
class EditBoutiqueDes(APIView):
	def post(self,request,*args,**kwargs):
		boutique=Boutique.objects.get(user=request.user)
		data=request.data
		boutique.description=data['description']
		boutique.save()
		serializer=BoutiqueSerializer(boutique)
		return Response({'message':'description bien editee'})

#Toutes les categories
class DisplayPerCategory(APIView):
	permission_classes = [permissions.AllowAny]
	def post(self,request):
		data=request.data
		cat=data['category']
		category=Category.objects.get(category=cat)
		produit=Produit.objects.filter(category=category,vendu=False,active=True,recycler=False,desactiver=False).order_by('-id')
		serializer=ProductSerializer(produit,many=True)
		return Response(serializer.data)
				
#Recuperation d un produit	
class GetProduit(APIView):
	permission_classes = [permissions.AllowAny]
	def post(self,request):
		data=request.data
		slug=data['slug']
		produit=Produit.objects.get(slug=slug)
		serializer=ProductSerializer(produit)
		return Response(serializer.data)
####
#Reuperation produit et cartproduit
class GetCartCommande(APIView):
	def post(self,request):
		data=request.data
		#slug=data['slug'] 
		id=data['id']
		cartproduit=CartProduct.objects.get(id=id)
		cartserial=CartProductSerializer(cartproduit)
		adress=Adress.objects.filter(bureau=False).order_by('-id')
		adressserial=AdresseSerializer(adress,many=True)
		return Response({'cartproduit':cartserial.data,'adress':adressserial.data})

#Calcul de la livraison
class CalculLivraison(APIView):
	def post(self,request):
		data=request.data
		adress_id=data['adress_id']
		cart_id=data['cartproduit_id']
		cartproduit=CartProduct.objects.get(id=cart_id)
		adress=Adress.objects.get(id=adress_id)
		poids=cartproduit.product.poids
		mesure=cartproduit.product.unite_mesure_poids
		if mesure=="g":
			vraipoids=int(poids/1000)
		else:
			vraipoids=int(poids)
		#print(vraipoids)
		produit=cartproduit.product
		if produit.region.id==adress.region.id:
			if adress.banlieu==True:
				if vraipoids<5:
					livraison=round(decimal.Decimal(2500),2)
					total=livraison + cartproduit.subtotal
					return Response({'livraison':livraison,'total':total})
				else:
					surpluspoids=vraipoids-5
					fraispoids=round(decimal.Decimal(2500*surpluspoids*5/100),2)
					livraison=fraispoids+2500
					total=livraison + cartproduit.subtotal
					return Response({'livraison':livraison,'total':total})
			else:
				if vraipoids<5:
					livraison=round(decimal.Decimal(2000),2)
					total=livraison + cartproduit.subtotal
					return Response({'livraison':livraison,'total':total})
				else:
					surpluspoids=vraipoids-5
					fraispoids=round(decimal.Decimal(2000*surpluspoids*5/100),2)
					livraison=fraispoids+2000
					total=livraison + cartproduit.subtotal
					return Response({'livraison':livraison,'total':total})

		else:
			if vraipoids<5:
				livraison=round(decimal.Decimal(4000),2)
				total=livraison + cartproduit.subtotal
				return Response({'livraison':livraison,'total':total})
			else:
				surpluspoids=vraipoids-5
				fraispoids=round(decimal.Decimal(4000*surpluspoids*5/100),2)
				livraison=fraispoids+4000
				total=livraison + cartproduit.subtotal
				return Response({'livraison':livraison ,'total':total})

class GetCommandeApayer(APIView):
	def post(self,request):
		id=request.data.get(id=id)
		commande=Commande.objects.get(id=id,acheteur=request.user)
		serializer=CommandeSerializer(commande)
		return Response(serializer.data)



#Produitvendu de l utilisateur		 		
class ProdutVendu(generics.ListAPIView):
	pagination_class =MyPaginationClass
	serializer_class=CommandeSerializer
	
	def get_queryset(self, *args, **kwargs):
		user=self.request.user
		produits=Produit.objects.filter(vendeur=user,vendu=True,recycler=False,desactiver=False).order_by('-id')
		return produits


#Historique d achat 
class ProduitAchete(generics.ListAPIView): 
	pagination_class =MyPaginationClass
	serializer_class=CommandeSerializer
	def get_queryset(self, *args, **kwargs):
		user=self.request.user
		produits=Commande.objects.filter(acheteur=user,statut_commande="produit livré").order_by('-id')
		return produits


#Commandes pas encore livrees
class CommandeEnCours(generics.ListAPIView):
	pagination_class =MyPaginationClass
	serializer_class=CommandeSerializer
	def get_queryset(self, *args, **kwargs):
		user=self.request.user
		commandes=Commande.objects.filter(acheteur=user,active=True).exclude(statut_commande="produit livré")
		return commandes


class ActifVendeur(APIView):
	def post(self,request):
		slug=request.data.get('slug')
		boutique=Boutique.objects.get(slug=slug)
		user=boutique.user
		if user.active==True:
			return Response(True)
		return Response(False)


class GetVendeur(APIView):
	def post(self,request):
		slug=request.data.get('slug')
		produit=Produit.objects.get(slug=slug)
		user=produit.vendeur
		serializer=UserSerializer(user)
		return Response(serializer.data)

###
class NoteVendeur(ModelViewSet):
	queryset=Boutique.objects.all()
	serializer_class=BoutiqueSerializer
	#permission_classes=(VendeurPermission,)
	@action(methods=["put"], detail=False, url_path='note')
	def noter(self,request,*args,**kwargs):
		id=request.data['id']
		note=int(request.data['note'])
		user=User.objects.get(id=id)
		boutique=Boutique.objects.get(user=user)
		boutique.note_vendeur=(boutique.note_vendeur+note)//2
		boutique.save()
		return Response({'message':'vendeur bien noté'})

###
class NosVendeurs(APIView):
	permission_classes = [permissions.AllowAny]
	def get(self,request):
		boutique=Boutique.objects.filter(active=True).order_by('-note_vendeur')[:5]
		serializer=BoutiqueSerializer(boutique,many=True)
		return Response(serializer.data)

#Les produits d Occasions		
class Occasions(APIView):
	permission_classes = [permissions.AllowAny]
	def get(self,request):
		occasion=Produit.objects.filter(category__category='Occasions',active=True,
			recycler=False,desactiver=False).order_by('-id')[:8]
		serializer=ProductSerializer(occasion,many=True)
		return Response(serializer.data)


#Produit d occassion
class ProduitOccasion(generics.ListAPIView):
	pagination_class =MyPaginationClass
	serializer_class=ProductSerializer
	permission_classes = [permissions.AllowAny]

	def get_queryset(self, *args, **kwargs):
		produits=Produit.objects.filter(category__category="Occasions",
		active=True,recycler=False,desactiver=False).order_by('-id')
		return produits

#Page meilleur vendeur
class PageMeilleurVendeur(generics.ListAPIView):
	pagination_class =MyPaginationClass
	serializer_class=BoutiqueSerializer
	permission_classes = [permissions.AllowAny]

	def get_queryset(self, *args, **kwargs):
		boutique=Boutique.objects.filter(active=True).order_by('-note_vendeur')
		return boutique

class NoterLeVendeur(APIView):
	def post(self,request): 
		id=request.data.get('id')
		note=round(decimal.Decimal(request.data.get('note')),1)
		notif=Notification.objects.get(id=id)
		command=notif.commande
		if command.produitcommande.product is None:
			boutique=command.produitcommande.imageproduct.produit.boutique
			boutique.note_vendeur=(boutique.note_vendeur+note)/2
			boutique.save()
			notif.active=False
			notif.save()
		else:
			boutique=command.produitcommande.product.boutique
			boutique.note_vendeur=(boutique.note_vendeur+note)/2
			boutique.save()
			notif.active=False
			notif.save()
		return Response({'success':'note'})


class LierSonCompteMoney(APIView):
	def post(self,request):
		phone=request.data.get('phone')
		boutique=Boutique.objects.get(user=request.user)
		boutique.comptegaalguimoney=phone
		boutique.save()
		return Response({'success':'boutique phone edit'})






		

		



	
		
		




  


		

		
	

	

		
		
		
	



	
		


	



	
	


	

	
	


			

		

		
		



























