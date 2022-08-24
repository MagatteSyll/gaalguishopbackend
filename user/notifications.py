from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import*
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message




def notif(user,data):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(user.group, {
    'type': 'notify',
    'value': data
    }) 

def NotifcationChangementEtatCommande(commande):
	message='L etat actuel de votre commande'+" " + commande.produitcommande.product.nom + " " +  'est: ' +" "+ commande.statut_commande +"."
	data={'titre':'Notification sur la commande'+" " + commande.produitcommande.product.nom,'body':message}
	Notification.objects.create(user=commande.acheteur,message=message,nature_notification='etat commande',
		commande=commande)
	devices = FCMDevice.objects.filter(user=commande.acheteur)
	for device in devices:
		device.send_message(Message(data=data))

def NotificationCommandeAuVendeur(commande):
	message='Votre produit'+" " +  commande.produitcommande.product.nom + " " +  'a été commandé  ' +" "+"rendez vous au point d acces le plus proche pour le déposer." 
	Notification.objects.create(user=commande.produitcommande.product.vendeur,message=message,nature_notification='vente',commande=commande)
	data={'titre':'Notification de vente du produit'+" " + commande.produitcommande.product.nom,'body':message}
	#notif(commande.produitcommande.product.vendeur,data)
	devices = FCMDevice.objects.filter(user=commande.produitcommande.product.vendeur)
	for device in devices:
		device.send_message(Message(data=data))
	 
	 

def AvertissementVendeur(user):
	message='L equipe GaalguiShop vous envoie cette notification d avertissment suite a un non respect de la politique de confidentialité.'
	data={'titre':'Notification d avertissment ','body':message}
	Notification.objects.create(user=user,message=message,
		nature_notification='avertissement')
	

def DesactivationDeBoutique(user):
	message='L équipe GaalguiShop vous envoie cette notification pour vous informer de la désactivation de votre boutique pour non respect de la politique de confidentialité.'
	data={'titre':'Désactivation de votre boutique ','body':message}
	Notification.objects.create(user=user,message=message,nature_notification='desactivation boutique')
	devices = FCMDevice.objects.filter(user=user)
	for device in devices:
		device.send_message(Message(data=data))


def AnnulationAchatCoteClient(commande):
	message=' Suite a un contre temps ,l équipe GaalguiShop vous envoie cette notification pour vous informer de l annulation de votre commande'+" "+ commande.produitcommande.product.nom +" "+".Un remboursement vous sera fait dans les plus brefs delais."
	data={'titre':'Annulation de commande ','body':message}
	Notification.objects.create(user=commande.acheteur,message=message,nature_notification='annulation d achat',commande=commande)
	devices = FCMDevice.objects.filter(user=commande.acheteur)
	for device in devices:
		device.send_message(Message(data=data))

def AnnulationVente(commande):
	message='L équipe GaalguiShop vous envoie cette notification pour vous informer de l annulation de l achat de votre produit'+" "+commande.produitcommande.product.nom + " "+ "et vous invite a plus de respect de la politique de confidentialité."
	data={'titre':'Annulation d achat','body':message}
	Notification.objects.create(user=commande.produitcommande.product.vendeur,message=message,nature_notification='annulation de vente',commande=commande)
	devices = FCMDevice.objects.filter(user=commande.produitcommande.product.vendeur)
	for device in devices:
		device.send_message(Message(data=data))



def NotificationNewProductToFollower(produit):
	message=produit.vendeur.prenom + " "+ produit.vendeur.nom +" " + "a ajouté un nouveau produit"+" "+ produit.nom
	data={'titre':'Un nouveau produit ','body':message}
	for follower in produit.boutique.follower.all():
		Notification.objects.create(user=follower.user,message=message,nature_notification='pour follower'
			,produit=produit)
		devices = FCMDevice.objects.filter(user=follower.user)
		for device in devices:
			device.send_message(Message(data=data))

def NotificationActivationBoutique(user):
	message='L équipe GaalguiShop vous envoie cette notification pour vous informer de la réactivation de votre boutique'
	data={'titre':'Reactivation boutique','body':message}
	Notification.objects.create(user=user,message=message,nature_notification="reactivation boutique")
	notif(user,data)

def NotificationProblemeTeechnique(probleme,users):
	for user in users:
		Notification.objects.create(user=user,message=probleme,nature_notification="probleme technique")
		data={'titre':'Signal d un probleme technique','body':probleme}
		devices = FCMDevice.objects.filter(user=user)
		for device in devices:
			device.send_message(Message(data=data))

def NotificationNoteVendeur(commande):
	message="Vous avez recemment achete le produit" + " " + commande.produitcommande.product.nom + " " + "vous pouvez noter le vendeur sur la qualite du produit"
	data={'titre':'Noter le vendeur','body':message}
	Notification.objects.create(user=commande.acheteur,message=message,nature_notification="note vendeur",commande=commande)
	devices = FCMDevice.objects.filter(user=commande.acheteur)
	for device in devices:
		device.send_message(Message(data=data))





