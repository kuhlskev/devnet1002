# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile for 2 CSR Routers and a JumpHost Ubuntu box
# For the session we will use kuhlskev/ansible_host container at dockerhub

Vagrant.configure("2") do |config|
    config.vm.define "rtr1" do |node|
      node.vm.box = "iosxe1002"
      node.vm.network "private_network", 
        ip: "172.20.20.10",
        auto_config: false
      node.vm.network "private_network", 
        virtualbox__intnet: "link1", 
        auto_config: false

      # attach a configuration disk
      node.vm.provider "virtualbox" do |v|
        v.customize ["storageattach", :id, 
          "--storagectl", "IDE_Controller", 
          "--port", 1, 
          "--device", 0, 
          "--type", "dvddrive", 
          "--medium", "rtr1.iso"
        ]
        #v.customize ["modifyvm", :id, 
        #  "--uart1", "0x3F8", 4, 
        #  "--uartmode1", 'tcpserver', 65000
        #]
      end
    end

    config.vm.define "rtr2" do |node|
      node.vm.box = "iosxe1002"
      node.vm.network "private_network", 
        ip: "172.20.20.20",
        auto_config: false
      node.vm.network "private_network", 
        virtualbox__intnet: "link1", 
        auto_config: false

      # attach a configuration disk
      node.vm.provider "virtualbox" do |v|
        v.customize ["storageattach", :id, 
          "--storagectl", "IDE_Controller", 
          "--port", 1, 
          "--device", 0, 
          "--type", "dvddrive", 
          "--medium", "rtr2.iso"
        ]
        #v.customize ["modifyvm", :id, 
        #  "--uart1", "0x3F8", 4, 
        #  "--uartmode1", 'tcpserver', 65001
        #]
      end
    end
    #config.vm.define "jh" do |node|
    #  node.vm.box = "ubuntu/trusty64"
    #  node.vm.box_version = "20160610.0.0"
    #  node.vm.box_check_update = false
    #  node.vm.provider :virtualbox do |v|
    #    v.customize ["modifyvm", :id, "--memory", 1024]
    #  end
    #  node.vm.synced_folder ".", "/home/vagrant"
    #  node.vm.provision "shell", inline: <<-SHELL
    #    sudo apt-get update
    #    sudo apt-get install build-essential libssl-dev libffi-dev libyaml-dev python-dev python-pip -y
    #    sudo pip install --upgrade pip
    #    sudo pip install --upgrade ndg-httpsclient
    #    sudo pip install -r /home/vagrant/nestconf/requirements.txt
    #    sudo pip install --upgrade setuptools --user python
    #    sudo pip install ciscoconfparse
    #    echo "cd /home/vagrant/nestconf" >> /home/vagrant/.bash_profile
    #  SHELL
    #end
end
