# devnet1002
This is a repo to accompany the DevNet 1002 Session for Cisco Live

To Follow along the exercises on your own you will need:
Git client
VirtualBox 5.0.28
Docker 1.13.1
Vagrant 1.8.7 (be aware of this issue)
cdrtools (in particular mkisofs)
a build environment (e.g. compiler, make, ...), suggest to use MacPorts or Brew if running on a Mac
Clone the https://github.com/ios-xr/iosxrv-x64-vbox repository from GitHub 
IOS XE image from Cisco.com (https://software.cisco.com/download/type.html?mdfid=284364978&catid=null, then go to IOS XE Software and download the Denali-16.3.2 .iso file in the Latest tree branch, ~350MB in size)

Go to the directory where you cloned the iso-xrv-x64-vbox repository. 
Create the Vagrant box image build by running the following command:
iosxe_iso2vbox.py -v ~/Downloads/csr1000v-universalk9.16.03.02.iso 
This will take a while. When done, you need to install the resulting box into Vagrant:
vagrant box add --name iosxe csr1000v-universalk9.16.03.02.box 
(See the output at the end of the script. It has the exact location of the generated box file and also the command to add / replace the Vagrant box file).

Clone this repo from GitHub into a new directory: https://github.com/kuhlskev/devnet1002
Make sure that the Vagrant box name matches the one configured in the Vagrant file
Ensure you have the required tools installed
run make to create the ISO files with the router configurations
Bring up the routers using vagrant up (brings up both) or vagrant up rtr1 to only start rtr1
Run the kuhlskev/ansible_host docker container (or you can install components, see Dockerfile for prerequisites)
you can see the setup.sh script to bring up the router and docker container as in the session
