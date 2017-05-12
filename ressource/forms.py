from django import forms
from django.contrib.auth.models import User

from .models import Ressources,Storages,Vnet,Subnet,Nic,VirtualMachine


class RessourcesForm(forms.ModelForm):

    class Meta:
        model = Ressources
        fields = ['groupe_name', 'location']

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class StoragesForm(forms.ModelForm):
    class Meta:
        model = Storages
        fields = ['storage_account_name']

class VnetForm(forms.ModelForm):
    class Meta:
        model = Vnet
        fields = ['vnet_name', 'location', 'address_prefixes']


class SubnetForm(forms.ModelForm):
    class Meta:
        model = Subnet
        fields = ['subnet_name','address_prefixes','vnet']


class NicForm(forms.ModelForm):
    class Meta:
        model = Nic
        fields = ['nic_name','location','ip_configuration_name','subnet','vnet']


class VirtualMachineForm(forms.ModelForm):
    class Meta:
        model = VirtualMachine
        fields = ['vm_name','location','vm_reference','storage','nic','os_disk_name']