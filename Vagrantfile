# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile for a CSR 1000V router and a Nexus 9000v switch
# For the session we will use kuhlskev/ansible_host container at dockerhub

Vagrant.configure("2") do |config|
    config.vm.define "rtr1" do |node|
      node.vm.box = "iosxe/16.09.01"
      # Explicity set SSH Port to avoid conflict and for provisioning
      node.vm.network :forwarded_port, guest: 22, host: 2222, id: 'ssh', auto_correct: true
      # Forward API Ports
      node.vm.network :forwarded_port, guest: 80, host: 2280, id: 'http', auto_correct: true
      node.vm.network :forwarded_port, guest: 443, host: 2443, id: 'https', auto_correct: true
      node.vm.network :forwarded_port, guest: 830, host: 2830, id: 'netconf', auto_correct: true      

      node.vm.network "private_network",
        ip: "172.20.20.10",
        name: "vboxnet5",
        auto_config: false,
        nic_type: "virtio"
      node.vm.network "private_network", 
        virtualbox__intnet: "link1", 
        auto_config: false,
        nic_type: "virtio" 
      
      # attach a configuration disk
      node.vm.provider "virtualbox" do |v|
        v.customize ["storageattach", :id, 
          "--storagectl", "IDE_Controller", 
          "--port", 1, 
          "--device", 0, 
          "--type", "dvddrive", 
          "--medium", "rtr1.iso"
        ]
        v.customize ["modifyvm", :id, "--memory", 3072]
      end
    end

    config.vm.define "n9kv1" do |n9kv1|
      n9kv1.vm.box = "nxos/9.3.3"
      n9kv1.ssh.insert_key = false
      n9kv1.vm.boot_timeout = 420
      n9kv1.vm.synced_folder '.', '/vagrant', disabled: true
      # Explicity set SSH Port to avoid conflict and for provisioning
      n9kv1.vm.network :forwarded_port, guest: 22, host: 3122, id: 'ssh', auto_correct: true
      # Forward API Ports
      n9kv1.vm.network :forwarded_port, guest: 80, host: 3180, id: 'http', auto_correct: true
      n9kv1.vm.network :forwarded_port, guest: 443, host: 3143, id: 'https', auto_correct: true
      n9kv1.vm.network :forwarded_port, guest: 830, host: 3130, id: 'netconf', auto_correct: true      

      n9kv1.vm.network "private_network", ip: "172.20.20.50", name: "vboxnet5", auto_config: false
      n9kv1.vm.network "private_network", auto_config: false, virtualbox__intnet: "nxosv_network2"
      n9kv1.vm.network "private_network", auto_config: false, virtualbox__intnet: "nxosv_network3"

      n9kv1.vm.provider :virtualbox do |vb|
        vb.customize ["modifyvm", :id, "--memory", 8192]
        vb.customize ['modifyvm',:id,'--nicpromisc2','allow-all']
        vb.customize ['modifyvm',:id,'--nicpromisc3','allow-all']
        vb.customize ['modifyvm',:id,'--nicpromisc4','allow-all']
        vb.customize "pre-boot", [
                "storageattach", :id,
                "--storagectl", "SATA",
                "--port", "1",
                "--device", "0",
                "--type", "dvddrive",
                "--medium", "nxosconfig.iso",
        ]
        end
    end  
end
