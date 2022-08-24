from django.contrib import admin
from .models import*




class CategoryAdmin(admin.ModelAdmin):
	list_display=['category']
	search_fields=['category']
	class Meta:
		model=Category


class FollowerAdmin(admin.ModelAdmin):
	list_display=['get_user']

	class Meta:
		model=Follower

	@admin.display(empty_value='???')
	def get_user(self, obj):
		return obj.user.prenom+" "+ obj.user.nom


class DeviseAdmin(admin.ModelAdmin):
	list_display=['devise']
	search_fields=['devise']
	class Meta:
		model=Devise
		

class BoutiqueAdmin(admin.ModelAdmin):
	list_display=['get_user','note_vendeur']
	search_fields=['note_vendeur']
	class Meta:
		model=Boutique

	@admin.display(empty_value='???')
	def get_user(self, obj):
		return obj.user.prenom+" "+ obj.user.nom

class ProduitAdmin(admin.ModelAdmin):
	list_display=['nom','prix','active','vendu']
	search_fields=['nom','prix']
	class Meta:
		model=Produit

class ProduitImageAdmin(admin.ModelAdmin):
	list_display=['get_produit','active','quantite']
	class Meta:
		model=ProduitImage

	@admin.display(empty_value='???')
	def get_produit(self, obj):
		return obj.produit.nom



class CartProductAdmin(admin.ModelAdmin):
	list_display=['get_produit','get_user','quantity']
	#search_fields=['product__nom']
	class Meta:
		model=CartProduct

	@admin.display(empty_value='???')
	def get_user(self, obj):
		return obj.client.prenom+" "+ obj.client.nom

	@admin.display(empty_value='???')
	def get_produit(self, obj):
		return obj.product.nom


class CartAdmin(admin.ModelAdmin):
	list_display=['get_user']
	#search_fields=['propri']
	class Meta:
		model=CartProduct
		
	@admin.display(empty_value='???')
	def get_user(self, obj):
		return obj.proprietaire .prenom+" "+ obj.proprietaire .nom


class CommandeAdmin(admin.ModelAdmin):
	list_display=['nom_client','phone','total']
	class Meta:
		model=Commande


admin.site.register(Category,CategoryAdmin)
admin.site.register(Produit,ProduitAdmin)
admin.site.register(CartProduct,CartProductAdmin)
admin.site.register(Cart,CartAdmin)
admin.site.register(Commande,CommandeAdmin)
admin.site.register(Boutique,BoutiqueAdmin)
admin.site.register(ProduitImage,ProduitImageAdmin)
admin.site.register(Devise,DeviseAdmin)
admin.site.register(Follower,FollowerAdmin)




