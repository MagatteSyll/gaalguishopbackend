from django.urls import path,include
from .views import*
from rest_framework.routers import SimpleRouter



router=SimpleRouter()
router.register('cartmanage',CartProductDeleteSingle)
router.register('produitmanage',Manageproduit)
router.register('rating',NoteVendeur)
router.register('commandemanage', RemoveCommande)
router.register('follower', RemoveFollower)
router.register('actioncommande',AnnulationCommande)

 

urlpatterns=[
    path('',include(router.urls)),
    path('region/',RegionList.as_view()),
    path('category/',CategoryList.as_view()), 
    path('addcart/',AddCartView.as_view()),
    path('cartview/',CartView.as_view()),
    path('ajoutdetailproduit/',AjoutDetailProduit.as_view()),
    path('ajoutimageproduit/',AjoutImageProduit.as_view()),
    path('getcart/',GetPanier.as_view()),
    path('adress/',AdressList.as_view()),
    path('commande/',PostCommande.as_view()),
    path('getproduitdetail/',GetDetailProduit.as_view()),#nouveau
    path('maboutique/',BoutiqueView.as_view()),
    path('profilboutiquevuclient/',BoutiqueVuClient.as_view()),
    path('editboutiquepic/',EditBoutiquePic.as_view()),
    path('editboutiquedes/',EditBoutiqueDes.as_view()),
    path('produitpercategory/',DisplayPerCategory.as_view()),
    path('singleproduit/',GetProduit.as_view()),
    path('historiquevente/',ProdutVendu.as_view()),
    path('historiquedachat/',ProduitAchete.as_view()),
    path('commandeencours/',CommandeEnCours.as_view()),
    path('profilevendeur/',ProfileVendeur.as_view()),
    path('activationcommande/',ActivationCommande.as_view()),
    path('actifvendeur/',ActifVendeur.as_view()),
    path('getvendeur/',GetVendeur.as_view()),
    path('search/',ProduitSearch.as_view()),
    path('nosvendeur/',NosVendeurs.as_view()),
    path('produitoccasion/',Occasions.as_view()),
    path('reactivationproduit/',ReactivationProduit.as_view()),
    path('cartcommande/',GetCartCommande.as_view()),
    path('calculivraison/',CalculLivraison.as_view()),
    path('getcommande/',GetCommande.as_view()),
    path('getnotification/',NotificationDetail.as_view()),
    path('addfollower/',AddFollower.as_view()),
    path('commandepay/',CommandePay.as_view()),
    path('confirmationpaycommande/',ConfirmationPayCommande.as_view()),
    path('noterlevendeur/',NoterLeVendeur.as_view()),
    path('getproduitcategory/<int:pk>/',ProduitCategory.as_view()),
    path('produitduneboutique/<int:pk>/',ProduitBoutique.as_view()),
    path('produitboutiqueparlevendeur/',ProduitBoutiqueVendeur.as_view()),
    path('deviselocationcategory/',GetdeviseLocationCategorie.as_view()),
    path('getproduitandimage/',GetProduitAndImages.as_view()),
    path('notifytofollower/',NotifyToFollower.as_view()),
    path('getcommandeapayer/',GetCommandeApayer.as_view()),
    path('getdetailcommande/',GetCommandeDetail.as_view()),
    path('pageproduitoccasion/',ProduitOccasion.as_view()),
    path('pagemeilleurvendeur/',PageMeilleurVendeur.as_view()),
    path('liersoncomptegaalguimoney/',LierSonCompteMoney.as_view())
    
 


    

    


    ]



   
