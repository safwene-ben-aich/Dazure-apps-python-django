from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import RessourcesForm,UserForm,StoragesForm,VnetForm,SubnetForm,NicForm,VirtualMachineForm
from .models import Ressources,User,UserCloud,Storages,Vnet,Subnet,Nic,VirtualMachine

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from haikunator import Haikunator
haikunator = Haikunator()


VM_REFERENCE = {
    'linux': {
        'publisher': 'Canonical',
        'offer': 'UbuntuServer',
        'sku': '16.04.0-LTS',
        'version': 'latest'
    },
    'windows': {
        'publisher': 'MicrosoftWindowsServerEssentials',
        'offer': 'WindowsServerEssentials',
        'sku': 'WindowsServerEssentials',
        'version': 'latest'
    }
}

def create_ressource(request):
    if not request.user.is_authenticated():
        return render(request, 'ressource/login.html')
    else:
        form = RessourcesForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            ressource = form.save(commit=False)
            ressource.user = request.user

            userCloud = get_object_or_404(UserCloud, user=(request.user))
            subscription_id = userCloud.subscription_id  # your Azure Subscription Id
            credentials = ServicePrincipalCredentials(
                client_id=userCloud.client_id,
                secret=userCloud.secret,
                tenant=userCloud.tenant
            )

            client = ResourceManagementClient(credentials, subscription_id)
            resource_group_params = {'location': form.cleaned_data['location']}
            print('Create Resource Group')
            client.resource_groups.create_or_update(form.cleaned_data['groupe_name'], resource_group_params)
            ressource.save()
            return render(request, 'ressource/detail_ressource.html', {'ressource': ressource})
        context = {
            "form": form,
        }
        return render(request, 'ressource/create_ressource.html', context)



def delete_ressource(request, ressource_id):
    ressource = Ressources.objects.get(pk=ressource_id)

    userCloud = get_object_or_404(UserCloud, user=(request.user))
    subscription_id = userCloud.subscription_id  # your Azure Subscription Id
    credentials = ServicePrincipalCredentials(
        client_id=userCloud.client_id,
        secret=userCloud.secret,
        tenant=userCloud.tenant
    )

    resource_client = ResourceManagementClient(credentials, subscription_id)
    delete_async_operation = resource_client.resource_groups.delete(ressource.groupe_name)
    delete_async_operation.wait()

    ressource.delete()
    ressource = Ressources.objects.filter(user=request.user)
    return render(request, 'ressource/index.html', {'ressources': ressource})




def create_virtualMachine(request, ressource_id):
    form = VirtualMachineForm(request.POST or None, request.FILES or None)
    ressource = get_object_or_404(Ressources, pk=ressource_id)
    if form.is_valid():
        ressource_vm = ressource.virtualmachine_set.all()
        for s in ressource_vm:
            if s.vm_name == form.cleaned_data.get("vm_name"):
                context = {
                    'ressource': ressource,
                    'form': form,
                    'error_message': 'You already added that Virtual Machine',
                }
                return render(request, 'ressource/create_virtualMachine.html', context)
        vm = form.save(commit=False)
        vm.ressource = ressource

        userCloud = get_object_or_404(UserCloud, user=(request.user))
        subscription_id = userCloud.subscription_id  # your Azure Subscription Id
        credentials = ServicePrincipalCredentials(
            client_id=userCloud.client_id,
            secret=userCloud.secret,
            tenant=userCloud.tenant
        )
        compute_client = ComputeManagementClient(credentials, subscription_id)
        network_client = NetworkManagementClient(credentials, subscription_id)

        #Get The nic ID
        nic = network_client.network_interfaces.get(vm.ressource.groupe_name,vm.nic.nic_name)


        print('\nCreating Virtual Machine')
        vm_parameters = create_vm_parameters(nic.id,VM_REFERENCE[vm.vm_reference],vm)
        async_vm_creation = compute_client.virtual_machines.create_or_update(
            vm.ressource.groupe_name, vm.vm_name, vm_parameters)
        async_vm_creation.wait()

        vm.save()
        return render(request, 'ressource/detail_ressource.html', {'ressource': ressource})
    context = {
        'ressource': ressource,
        'form': form,
    }
    return render(request, 'ressource/create_virtualMachine.html', context)

def delete_virtualMachine(request, ressource_id, virtualMachine_id):
    ressource = get_object_or_404(Ressources, pk=ressource_id)
    vm = VirtualMachine.objects.get(pk=virtualMachine_id)

    userCloud = get_object_or_404(UserCloud, user=(request.user))
    subscription_id = userCloud.subscription_id  # your Azure Subscription Id
    credentials = ServicePrincipalCredentials(
        client_id=userCloud.client_id,
        secret=userCloud.secret,
        tenant=userCloud.tenant
    )
    compute_client = ComputeManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)

    async_vm_delete = compute_client.virtual_machines.delete(vm.ressource.groupe_name,vm.vm_name)
    async_vm_delete.wait()
    vm.delete()
    return render(request, 'ressource/detail_ressource.html', {'ressource': ressource})


def create_storage(request, ressource_id):
    print(ressource_id)
    form = StoragesForm(request.POST or None, request.FILES or None)
    ressource = get_object_or_404(Ressources, pk=ressource_id)
    if form.is_valid():
        ressource_storages = ressource.storages_set.all()
        for s in ressource_storages:
            if s.storage_account_name == form.cleaned_data.get("storage_account_name"):
                context = {
                    'ressource': ressource,
                    'form': form,
                    'error_message': 'You already added that storage',
                }
                return render(request, 'ressource/create_storage.html', context)
        storages = form.save(commit=False)
        storages.ressource = ressource

        userCloud = get_object_or_404(UserCloud, user=(request.user))
        subscription_id = userCloud.subscription_id  # your Azure Subscription Id
        credentials = ServicePrincipalCredentials(
            client_id=userCloud.client_id,
            secret=userCloud.secret,
            tenant=userCloud.tenant
        )
        storage_client = StorageManagementClient(credentials, subscription_id)
        storage_async_operation = storage_client.storage_accounts.create(
            storages.ressource.groupe_name,
            form.cleaned_data['storage_account_name'],
            {
                'sku': {'name': 'standard_lrs'},
                'kind': 'storage',
                'location': storages.ressource.location
            }
        )
        storage_async_operation.wait()


        storages.save()
        return render(request, 'ressource/detail_ressource.html', {'ressource': ressource})
    context = {
        'ressource': ressource,
        'form': form,
    }
    return render(request, 'ressource/create_storage.html', context)

def delete_storage(request, ressource_id, storage_id):
    ressource = get_object_or_404(Ressources, pk=ressource_id)
    storage = Storages.objects.get(pk=storage_id)

    userCloud = get_object_or_404(UserCloud, user=(request.user))
    subscription_id = userCloud.subscription_id  # your Azure Subscription Id
    credentials = ServicePrincipalCredentials(
        client_id=userCloud.client_id,
        secret=userCloud.secret,
        tenant=userCloud.tenant
    )
    storage_client = StorageManagementClient(credentials, subscription_id)
    storage_client.storage_accounts.delete(storage.ressource.groupe_name,storage.storage_account_name)
    storage.delete()
    return render(request, 'ressource/detail_ressource.html', {'ressource': ressource})


def create_subnet(request, ressource_id):
    print(ressource_id)
    form = SubnetForm(request.POST or None, request.FILES or None)
    ressource = get_object_or_404(Ressources, pk=ressource_id)
    if form.is_valid():
        ressource_subnets = ressource.subnet_set.all()
        for s in ressource_subnets:
            if s.subnet_name == form.cleaned_data.get("subnet_name"):
                context = {
                    'ressource': ressource,
                    'form': form,
                    'error_message': 'You already added that subnet',
                }
                return render(request, 'ressource/create_subnet.html', context)
        subnet = form.save(commit=False)
        subnet.ressource = ressource

        userCloud = get_object_or_404(UserCloud, user=(request.user))
        subscription_id = userCloud.subscription_id  # your Azure Subscription Id
        credentials = ServicePrincipalCredentials(
            client_id=userCloud.client_id,
            secret=userCloud.secret,
            tenant=userCloud.tenant
        )
        network_client = NetworkManagementClient(credentials, subscription_id)

        async_subnet_creation = network_client.subnets.create_or_update(
            subnet.ressource.groupe_name,
            subnet.vnet.vnet_name,
            form.cleaned_data['subnet_name'],
            {'address_prefix': form.cleaned_data['address_prefixes']}
        )
        async_subnet_creation.wait()
        subnet.save()
        return render(request, 'ressource/detail_ressource.html', {'ressource': ressource})
    context = {
        'ressource': ressource,
        'form': form,
    }
    return render(request, 'ressource/create_subnet.html', context)


def delete_subnet(request, ressource_id, subnet_id):
    ressource = get_object_or_404(Ressources, pk=ressource_id)
    subnet = Subnet.objects.get(pk=subnet_id)

    userCloud = get_object_or_404(UserCloud, user=(request.user))
    subscription_id = userCloud.subscription_id  # your Azure Subscription Id
    credentials = ServicePrincipalCredentials(
        client_id=userCloud.client_id,
        secret=userCloud.secret,
        tenant=userCloud.tenant
    )
    network_client = NetworkManagementClient(credentials, subscription_id)

    async_subnet_creation = network_client.subnets.delete(subnet.ressource.groupe_name,subnet.vnet.vnet_name,subnet.subnet_name)
    async_subnet_creation.wait()



    subnet.delete()
    return render(request, 'ressource/detail_ressource.html', {'ressource': ressource})



def create_nic(request, ressource_id):
    print(ressource_id)
    form = NicForm(request.POST or None, request.FILES or None)
    ressource = get_object_or_404(Ressources, pk=ressource_id)
    if form.is_valid():
        ressource_nic = ressource.nic_set.all()
        for s in ressource_nic:
            if s.nic_name == form.cleaned_data.get("nic_name"):
                context = {
                    'ressource': ressource,
                    'form': form,
                    'error_message': 'You already added that nic',
                }
                return render(request, 'ressource/create_nic.html', context)
        nic = form.save(commit=False)
        nic.ressource = ressource

        userCloud = get_object_or_404(UserCloud, user=(request.user))
        subscription_id = userCloud.subscription_id  # your Azure Subscription Id
        credentials = ServicePrincipalCredentials(
            client_id=userCloud.client_id,
            secret=userCloud.secret,
            tenant=userCloud.tenant
        )
        network_client = NetworkManagementClient(credentials, subscription_id)


        subnet_infos = network_client.subnets.get(nic.ressource.groupe_name,nic.vnet.vnet_name,nic.subnet.subnet_name)




        async_nic_creation = network_client.network_interfaces.create_or_update(
            nic.ressource.groupe_name,
            form.cleaned_data['nic_name'],
            {
                'location': nic.ressource.location,
                'ip_configurations': [{
                    'name': form.cleaned_data['ip_configuration_name'],
                    'subnet': {
                        'id': subnet_infos.id
                    }
                }]
            }
        )
        print(nic.ressource.groupe_name)
        async_nic_creation.wait()
        nic.save()
        return render(request, 'ressource/detail_ressource.html', {'ressource': ressource})
    context = {
        'ressource': ressource,
        'form': form,
    }
    return render(request, 'ressource/create_nic.html', context)

def delete_nic(request, ressource_id, nic_id):
    ressource = get_object_or_404(Ressources, pk=ressource_id)
    nic = Nic.objects.get(pk=nic_id)

    userCloud = get_object_or_404(UserCloud, user=(request.user))
    subscription_id = userCloud.subscription_id  # your Azure Subscription Id
    credentials = ServicePrincipalCredentials(
        client_id=userCloud.client_id,
        secret=userCloud.secret,
        tenant=userCloud.tenant
    )
    network_client = NetworkManagementClient(credentials, subscription_id)

    async_nic_delete = network_client.network_interfaces.delete(nic.ressource.groupe_name,nic.nic_name)
    nic.delete()
    return render(request, 'ressource/detail_ressource.html', {'ressource': ressource})


def create_vnet(request, ressource_id):
    print(ressource_id)
    form = VnetForm(request.POST or None, request.FILES or None)
    ressource = get_object_or_404(Ressources, pk=ressource_id)
    if form.is_valid():
        ressource_vnets = ressource.vnet_set.all()
        for s in ressource_vnets:
            if s.vnet_name == form.cleaned_data.get("vnet_name"):
                context = {
                    'ressource': ressource,
                    'form': form,
                    'error_message': 'You already added that vnet',
                }
                return render(request, 'ressource/create_vnet.html', context)
        vnet = form.save(commit=False)
        vnet.ressource = ressource

        userCloud = get_object_or_404(UserCloud, user=(request.user))
        subscription_id = userCloud.subscription_id  # your Azure Subscription Id
        credentials = ServicePrincipalCredentials(
            client_id=userCloud.client_id,
            secret=userCloud.secret,
            tenant=userCloud.tenant
        )
        network_client = NetworkManagementClient(credentials, subscription_id)

        async_vnet_creation = network_client.virtual_networks.create_or_update(
            vnet.ressource.groupe_name,
            form.cleaned_data['vnet_name'],
            {
                'location': form.cleaned_data['location'],
                'address_space': {
                    'address_prefixes': [form.cleaned_data['address_prefixes']]
                }
            }
        )
        async_vnet_creation.wait()

        vnet.save()
        return render(request, 'ressource/detail_ressource.html', {'ressource': ressource})
    context = {
        'ressource': ressource,
        'form': form,
    }
    return render(request, 'ressource/create_vnet.html', context)


def delete_vnet(request, ressource_id, vnet_id):
    ressource = get_object_or_404(Ressources, pk=ressource_id)
    vnet = Vnet.objects.get(pk=vnet_id)

    userCloud = get_object_or_404(UserCloud, user=(request.user))
    subscription_id = userCloud.subscription_id  # your Azure Subscription Id
    credentials = ServicePrincipalCredentials(
        client_id=userCloud.client_id,
        secret=userCloud.secret,
        tenant=userCloud.tenant
    )
    network_client = NetworkManagementClient(credentials, subscription_id)

    async_vnet_creation = network_client.virtual_networks.delete(vnet.ressource.groupe_name,vnet.vnet_name)
    async_vnet_creation.wait()


    vnet.delete()
    return render(request, 'ressource/detail_ressource.html', {'ressource': ressource})



def index(request):
    ressource = Ressources.objects.filter(user=request.user)
    return render(request, 'ressource/index.html',{'ressources':ressource})



def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'ressource/login.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        #Authentification avec la base de données
        user = authenticate(username=username, password=password)

        #Autentfication avec Azure

        userCloud = get_object_or_404(UserCloud ,user=user)

        subscription_id = userCloud.subscription_id  # your Azure Subscription Id
        credentials = ServicePrincipalCredentials(
            client_id=userCloud.client_id,
            secret=userCloud.secret,
            tenant=userCloud.tenant
        )

        if user is not None:
            if user.is_active:
                login(request, user)
                ressources = Ressources.objects.filter(user=request.user)
                return render(request, 'ressource/index.html', {'ressources': ressources})
            else:
                return render(request, 'ressource/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'ressource/login.html', {'error_message': 'Invalid login'})
    return render(request, 'ressource/login.html')



def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                ressources = Ressources.objects.filter(user=request.user)
                return render(request, 'ressource/index.html', {'ressources': ressources})
    context = {
        "form": form,
    }
    return render(request, 'ressource/register.html', context)


def detail(request, ressource_id):
    if not request.user.is_authenticated():
        return render(request, 'ressource/login.html')
    else:

        user = request.user
        ressource = get_object_or_404(Ressources, pk=ressource_id)
        return render(request, 'ressource/detail_ressource.html', {'ressource': ressource, 'user': user})

def automation(request, ressource_id, operation_id):
    ressource = get_object_or_404(Ressources, pk=ressource_id)


    userCloud = get_object_or_404(UserCloud, user=(request.user))
    subscription_id = userCloud.subscription_id  # your Azure Subscription Id
    credentials = ServicePrincipalCredentials(
        client_id=userCloud.client_id,
        secret=userCloud.secret,
        tenant=userCloud.tenant
    )
    compute_client = ComputeManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)

    if operation_id == '1':
        for vm in compute_client.virtual_machines.list(ressource.groupe_name):
            compute_client.virtual_machines.power_off(ressource.groupe_name,vm.name)
    elif operation_id == '2':
        print()




    return render(request, 'ressource/automation.html', {'ressource': ressource})


def create_vm_parameters(nic_id, vm_reference,vm):
    """Create the VM parameters structure.
    """
    print(vm.ressource.user.password)
    return {
        'location': vm.location,
        'os_profile': {
            'computer_name': vm.vm_name,
            'admin_username':vm.ressource.user.username,
            'admin_password': '123456__pass'
        },
        'hardware_profile': {
            'vm_size': 'Standard_DS1'
        },
        'storage_profile': {
            'image_reference': {
                'publisher': vm_reference['publisher'],
                'offer': vm_reference['offer'],
                'sku': vm_reference['sku'],
                'version': vm_reference['version']
            },
            'os_disk': {
                'name': vm.os_disk_name,
                'caching': 'None',
                'create_option': 'fromImage',
                'vhd': {
                    'uri': 'https://{}.blob.core.windows.net/vhds/{}.vhd'.format(
                        vm.storage.storage_account_name, vm.vm_name+haikunator.haikunate())
                }
            },
        },
        'network_profile': {
            'network_interfaces': [{
                'id': nic_id,
            }]
        },
    }


