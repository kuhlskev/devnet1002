# mkisofs is part of cdrtools in MacPorts

ROUTER = rtr1 rtr2
ISOS = $(ROUTER:=.iso)
PORTS = ports.cfg

all: $(ISOS)

%.iso: %-confg
	cp $< iosxe_config.txt 
	mkisofs -l -o $@ iosxe_config.txt
	rm iosxe_config.txt

ports:
	touch $(PORTS)
	@for rtr in $(ROUTER); do \
	    vagrant port --machine-readable $$rtr | \
	    grep $$rtr >>ports.cfg; \
	done

clean:
	rm -f *.iso $(PORTS)
