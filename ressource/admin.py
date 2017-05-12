from django.contrib import admin
from .models import Ressources, Subnet, Nic, Storages, Vnet, UserCloud,VirtualMachine

admin.site.register(Ressources)
admin.site.register(Subnet)
admin.site.register(Nic)
admin.site.register(Storages)
admin.site.register(Vnet)
admin.site.register(UserCloud)
admin.site.register(VirtualMachine)
