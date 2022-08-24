from django.shortcuts import render
from rest_framework.permissions import  BasePermission, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from produit.serializer import*
from produit.models import*
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView,DestroyAPIView,GenericAPIView,ListAPIView
from rest_framework import filters
from rest_framework import authentication, permissions,generics
from user.models import*
from user.serializer import*
from user.notifications import*


 



class IsStaf(APIView):
	permission_classes=[permissions.AllowAny]
	def get(self,request):
		if request.user.is_staff==True:
			return Response(True)
		return Response(False)


class RechercheCommandes(APIView):
	permission_classes = [permissions.IsAdminUser]
	def post(self,request):
		id=request.data.get('id')
		commande=Commande.objects.get(id=id,active=True,payer=True,annuler=False)
		serializer=CommandeSerializer(commande)
		return Response(serializer.data)

class DepotCommande(APIView):
	permission_classes = [permissions.IsAdminUser]
	def post(self,request):
		data=request.data
		id=data['id'] 
		commande=Commande.objects.get(id=id) 
		commande.statut_commande="produit en cours de livraison "
		commande.save()
		NotifcationChangementEtatCommande(commande)
		action='Modification du status de la  commande : '+ " " + str(id)  + " " + 'nouveau status:' + commande.statut_commande
		employe=Employe.objects.get(user=request.user,active=True)
		ActionStaff.objects.create(employe=employe,action=action)
		return Response({"message":'produit status change'})


class RetraitCommande(APIView):
	permission_classes = [permissions.IsAdminUser]
	def post(self,request):
		data=request.data
		id=data['id']
		commande=Commande.objects.get(id=id)
		commande.statut_commande="produit livré"
		commande.save()
		user=commande.acheteur
		if commande.produitcommande.product.variation==True:
			commande.produitcommande.imageproduct.vendu=True
			commande.produitcommande.imageproduct.qte_vendu+=commande.produitcommande.quantity
			commande.produitcommande.imageproduct.save()
			prod=commande.produitcommande.imageproduct.produit
			prod.vendu_qte+=commande.produitcommande.quantity
			prod.vendu=True
			prod.save()
			NotificationNoteVendeur(commande)
		else:
			commande.produitcommande.product.vendu=True
			commande.produitcommande.product.vendu_qte+=commande.produitcommande.quantity
			commande.produitcommande.product.save()
			NotificationNoteVendeur(commande)
		action='Modification du status de la  commande : '+ " " +  str(id) + " " + 'nouveau status:' + commande.statut_commande
		employe=Employe.objects.get(user=request.user,active=True)
		ActionStaff.objects.create(employe=employe,action=action)
		return Response({"message":'produit status change'})
	
		
#Modification commande par le personnel de bureau
class ModificationEtatCommande(APIView):
	permission_classes=[permissions.IsAdminUser]
	def post(self,request):
		id=request.data.get('id')
		com=Commande.objects.get(id=id)
		etat=request.data.get('etat')
		com.statut_commande=etat
		com.save()
		action="modification du status de la commande au bureau " + " "+ str(id) + " " + " en " + " "+ etat
		employe=Employe.objects.get(user=request.user,active=True)
		ActionStaff.objects.create(action=action,employe=employe)
		return Response ({'success':'modification commande'})
		
#Annulation commande par le personnel de bureau		
class AnnulationCommande(APIView):
	permission_classes=[permissions.IsAdminUser]
	def post(self,request):
		id=request.data.get('id')
		motif=request.data.get('motif')
		commande=Commande.objects.get(id=id)
		commande.active=False
		##commande.payer
		commande.annuler=True
		commande.save() 
		action="Annulation de la  commande " + " " + str(id) + " " + " pour motif" + " " + motif
		employe=Employe.objects.get(user=request.user,active=True)
		ActionStaff.objects.create(employe=employe,action=action)
		AnnulationAchatCoteClient(commande)
		AnnulationVente(commande)
		serializer=CommandeSerializer(commande)
		return Response(serializer.data)

		 
  
class AvertirVendeur(APIView):
	permission_classes = [permissions.IsAdminUser]
	def post(self,request):
		id=request.data.get('id')
		motif=request.data.get('motif')
		boutique=Boutique.objects.get(id=id)
		boutique.avertissement+=1
		boutique.save()
		if boutique.avertissement<4:
			AvertissementVendeur(boutique.user)
		if boutique.avertissement>=4:
			boutique.active=False
			boutique.save()
			produit=Produit.objects.filter(vendeur=boutique.user)
			for p in produit:
				p.desactiver=True
				p.save()
				imgprod=ProduitImage.objects.filter(produit=p)
				for im in imgprod:
					im.desactiver=True
					im.save()
			DesactivationDeBoutique(boutique.user)
			boutique.nbredesactivation+=1
			boutique.save()
		action="avertissement de l utilisateur  numero" + " " + str(boutique.user.id) +" "+ "pour motif"+" "+ motif
		employe=Employe.objects.get(user=request.user,active=True)
		ActionStaff.objects.create(employe=employe,action=action) 
		return Response({'success':'avertissement vendeur'})


class DesactiverLeVendeur(APIView):
	permission_classes = [permissions.IsAdminUser]
	def post(self,request):
		id=request.data.get('id')
		motif=request.data.get('motif')
		boutique=Boutique.objects.get(id=id)
		boutique.active=False
		boutique.save()
		produit=Produit.objects.filter(vendeur=boutique.user)
		for p in produit:
			p.desactiver=True
			p.save()
			imgprod=ProduitImage.objects.filter(produit=p)
			for im in imgprod:
				im.desactiver=True
				im.save()
		DesactivationDeBoutique(boutique.user)
		action="Desactivation de la boutique  de l utilisateur  numero" + " " + str(boutique.user.id) +" "+ "pour motif"+" "+ motif
		employe=Employe.objects.get(user=request.user,active=True)
		ActionStaff.objects.create(employe=employe,action=action) 
		return Response({'success':'desactivation vendeur'})


class ReactivationVendeur(APIView):
	permission_classes=[permissions.IsAdminUser]
	def post(self,request):
		id=request.data.get('id')
		motif=request.data.get('motif')
		boutique=Boutique.objects.get(id=id)
		boutique.active=True
		boutique.avertissement=0
		boutique.save()
		produit=Produit.objects.filter(vendeur=boutique.user)
		for p in produit:
			p.desactiver=False
			p.save()
			imgprod=ProduitImage.objects.filter(produit=p)
			for im in imgprod:
				im.desactiver=False
				im.save()
		NotificationActivationBoutique(boutique.user)	
		action="reactivation  l utilisateur  numero" + " " + str(boutique.user.id) +" "+ "pour motif"+" "+ motif
		employe=Employe.objects.get(user=request.user,active=True)
		ActionStaff.objects.create(employe=employe,action=action) 
		return Response({'success':'reactivation vendeur'})
	

class GetBoutique(APIView):
	permission_classes = [permissions.IsAdminUser]
	def post(self,request):
		id=request.data.get('id')
		boutique=Boutique.objects.get(id=id)
		serializer=BoutiqueSerializer(boutique)
		return Response(serializer.data)


class ProblemeTechnique(APIView):
	permission_classes = [permissions.IsAdminUser]
	def post(self,request):
		probleme=request.data.get('probleme')
		users=User.objects.filter(is_staff=True,istechnique=True)
		NotificationProblemeTeechnique(probleme,users)
		action='Signal d un probleme technique' + " " + probleme
		employe=Employe.objects.get(user=request.user,active=True)
		ActionStaff.objects.create(action=action,employe=employe)
		return Response({'success':'probleme technique'})


class GetNotification(APIView):
	permission_classes = [permissions.IsAdminUser]
	def post(self,request):
		id=request.data.get('id')
		notif=Notification.objects.get(id=id)
		serializer=NotificationSerializer(notif)
		return Response(serializer.data)

		
		
	
		





	
