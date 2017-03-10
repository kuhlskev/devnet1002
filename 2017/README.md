# devnet1002
This is a repo to accompany the DevNet 1002 Session for Cisco Live

To Follow along the exercises on your own you will need:

- Git client
- VirtualBox 5.0.28
- Docker 1.13.1
- Vagrant 1.8.7 (be aware of this issue)
- cdrtools (in particular mkisofs)
- a build environment (e.g. compiler, make, ...), suggest to use MacPorts or Brew if running on a Mac
- Clone the [repository from GitHub](https://github.com/ios-xr/iosxrv-x64-vbox)
- [IOS XE image](https://software.cisco.com/download/type.html?mdfid=284364978&catid=null) from Cisco.com, then go to IOS XE Software and download the Denali-16.3.2 .iso file in the Latest tree branch, ~350MB in size)

1. Go to the directory where you cloned the iso-xrv-x64-vbox repository.
2. Create the Vagrant box image build by running the following command:

	`iosxe_iso2vbox.py -v ~/Downloads/csr1000v-universalk9.16.03.02.iso`

3. This will take a while. When done, you need to install the resulting box into Vagrant:

	`vagrant box add --name iosxe csr1000v-universalk9.16.03.02.box`

	(See the output at the end of the script. It has the exact location of the generated box file and also the command to add / replace the Vagrant box file).

4. Clone [this repo](https://github.com/kuhlskev/devnet1002) from GitHub into a new directory.

	`git clone https://github.com/kuhlskev/devnet1002`

5. Make sure that the Vagrant box name matches the one configured in the Vagrant file

6. Ensure you have the required tools installed

7. run `make` to create the ISO files with the router configurations

8. Bring up the routers using `vagrant up` (brings up both) or `vagrant up rtr1` to only start rtr1

9. Run the `kuhlskev/ansible_host` docker container (or you can install components, see Dockerfile for prerequisites)

	`docker run -it --rm -v$(pwd):/home/docker kuhlskev/ansible_host /bin/sh`

you can see the setup.sh script to bring up the router and docker container as in the session