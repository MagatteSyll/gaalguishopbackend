from django.contrib import admin
from .models import*




class UserAdmin(admin.ModelAdmin):
	list_display=['prenom', 'nom', 'phone', 'active',]
	search_fields=['prenom','nom', 'phone']
	class Meta:
		model=User

class PhoneConfirmationAdmin(admin.ModelAdmin):
	list_display=['phone', 'code','active']
	search_fields=['phone','code']
	class Meta:
		model=CodeConfirmationPhone

class NotificationAdmin(admin.ModelAdmin):
	list_display=['message', 'lu']
	search_fields=['message']
	class Meta:
		model=Notification

class PaysAdmin(admin.ModelAdmin):
	list_display=['pays',]
	search_fields=['pays']
	list_display_links=['pays']
	class Meta:
		model=Pays

class RegionAdmin(admin.ModelAdmin):
	list_display=['region', 'get_pays']
	search_fields=['message']
	class Meta:
		model=Region

	@admin.display(empty_value='???')
	def get_pays(self, obj):
		return obj.pays.pays


class AdressAdmin(admin.ModelAdmin):
	list_display=['adress', 'get_region','get_pays']
	search_fields=['message']
	#list_filter=[]
	class Meta:
		model=Adress


	@admin.display(empty_value='???')
	def get_region(self, obj):
		return obj.region.region

	@admin.display(empty_value='???')
	def get_pays(self, obj):
		return obj.region.pays.pays

class EmployeAdmin(admin.ModelAdmin):
	list_display=['get_employe', 'get_lieu_travail',]
	class Meta:
		model=Employe

	@admin.display(empty_value='???')
	def get_employe(self, obj):
		return obj.user.prenom+" "+obj.user.nom
	@admin.display(empty_value='???')
	def get_lieu_travail(self, obj):
		return obj.lieu_travail.adress
		


class ActionStaffAdmin(admin.ModelAdmin):
	list_display=['get_employe', 'get_lieu_travail',]
	search_fields=['message']
	class Meta:
		model=ActionStaff

	@admin.display(empty_value='???')
	def get_employe(self, obj):
		return obj.employe.user.prenom+" "+obj.employe.user.nom


	@admin.display(empty_value='???')
	def get_lieu_travail(self, obj):
		return obj.employe.lieu_travail.adress


admin.site.register(User,UserAdmin)
admin.site.register(Notification,NotificationAdmin)
admin.site.register(CodeConfirmationPhone,PhoneConfirmationAdmin)
admin.site.register(ActionStaff,ActionStaffAdmin)
admin.site.register(Pays,PaysAdmin)
admin.site.register(Region,RegionAdmin)
admin.site.register(Adress,AdressAdmin)
admin.site.register(Employe,EmployeAdmin)

