from django.contrib.auth.models import Permission, User
from django.db import models
from docutils.parsers.rst.directives import choice

LOCATIONS=(
    ('westus','West US'),
    ('westus2','West US2'),
    ('centralus','Central US'),
    ('eastasia', 'East Asia'),
    ('southeastasia','South East Asia'),
    ('eastus','East US'),
    ('eastus2','East US2'),
    ('northcentralus','North Central US'),
    ('southcentralus','South Central US'),
    ('westcentralus','West Central US'),
    ('northeurope','North Europoe'),
    ('westeurope','West Europe'),
    ('japaneast','Japan EAST'),
    ('japanwest','Japan WEST'),
    ('brazilsouth','Brazil South'),
    ('australiasoutheast','Australia South East'),
    ('australiaeast','Australia EAST'),
    ('westindia','West India'),
    ('southindia','South India'),
    ('centralindia','Central India'),
    ('canadacentral','Canada Central'),
    ('canadaeast','Canada East'),
    ('uksouth','UK South'),
    ('ukwest','UK West'),
    ('koreacentral','Korea Central'),
    ('koreasouth','Korea South')
)
ADDRESS_PREFIXES=(
    ('10.0.0.0/10', '10.0.0.0/10'),
    ('10.0.0.0/11', '10.0.0.0/11'),
    ('10.0.0.0/12', '10.0.0.0/12'),
    ('10.0.0.0/13', '10.0.0.0/13'),
    ('10.0.0.0/14', '10.0.0.0/14'),
    ('10.0.0.0/15', '10.0.0.0/15'),
    ('10.0.0.0/16', '10.0.0.0/16'),
    ('192.168.1.0/16', '192.168.1.0/16'),
    ('192.168.1.0/17', '192.168.1.0/17'),
    ('192.168.1.0/18', '192.168.1.0/18'),
    ('192.168.1.0/19', '192.168.1.0/19'),
    ('192.168.1.0/20', '192.168.1.0/20'),
    ('172.16.1.0/10', '172.16.1.0/10'),
    ('172.16.1.0/11', '172.16.1.0/11'),
    ('172.16.1.0/12', '172.16.1.0/12'),
    ('172.16.1.0/13', '172.16.1.0/13'),
    ('172.16.1.0/14', '172.16.1.0/14'),
    ('172.16.1.0/15', '172.16.1.0/15'),
    ('172.16.1.0/16', '172.16.1.0/16'),
)

VM_REFERENCE=(
    ('linux','linux'),
    ('windows','windows')
)


class Ressources(models.Model):
    user = models.ForeignKey(User,default=1)
    groupe_name = models.CharField(max_length=250,verbose_name="Groupe name")
    location = models.CharField(max_length=250, choices=LOCATIONS,default='westus',verbose_name='Location')

    def __str__(self):
        return self.groupe_name

class Storages(models.Model):
    ressource = models.ForeignKey(Ressources)
    storage_account_name = models.CharField(max_length=250,verbose_name="Storage account name")

    def __str__(self):
        return self.storage_account_name

class Vnet(models.Model):
    ressource = models.ForeignKey(Ressources)
    vnet_name = models.CharField(max_length=250,verbose_name="Virtual network name")
    location = models.CharField(max_length=250,choices=LOCATIONS, default='westus',verbose_name="Location")
    address_prefixes = models.CharField(max_length=250,choices=ADDRESS_PREFIXES,default='10.0.0.0/16',verbose_name="Address prefixes")

    def __str__(self):
        return self.vnet_name

class Subnet(models.Model):
    ressource = models.ForeignKey(Ressources)
    vnet = models.ForeignKey(Vnet)
    subnet_name = models.CharField(max_length=250)
    address_prefixes = models.CharField(max_length=250, choices=ADDRESS_PREFIXES, default='10.0.0.0/16')

    def __str__(self):
        return self.subnet_name

class Nic(models.Model):
    ressource = models.ForeignKey(Ressources)
    nic_name = models.CharField(max_length=250)
    location = models.CharField(max_length=250,choices=LOCATIONS, default='westus')
    ip_configuration_name = models.CharField(max_length=250)
    subnet = models.ForeignKey(Subnet)
    vnet = models.ForeignKey(Vnet)

    def __str__(self):
        return self.nic_name

class UserCloud(models.Model):
    user = models.OneToOneField(User)
    username_azure = models.CharField(max_length=500)
    password_azure = models.CharField(max_length=500)
    subscription_id = models.CharField(max_length=500)
    client_id = models.CharField(max_length=500)
    secret = models.CharField(max_length=500)
    tenant = models.CharField(max_length=500)

    def __str__(self):
        return self.subscription_id

class VirtualMachine(models.Model):
    ressource = models.ForeignKey(Ressources)
    nic = models.ForeignKey(Nic)
    storage = models.ForeignKey(Storages)
    vm_name = models.CharField(max_length=250,verbose_name="Virtual Machine name")
    location = models.CharField(max_length=250,choices=LOCATIONS,default='10.0.0.0/16',verbose_name="Location")
    vm_reference = models.CharField(max_length=250,choices=VM_REFERENCE,default='linux',verbose_name='Operating System')
    os_disk_name = models.CharField(max_length=250,default='os_disk_name')

