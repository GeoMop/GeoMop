GITDIR=..
VERSION=1.0.0b
PKGNAME=geomop

PKGDIR=$(PKGNAME)-$(VERSION)

clean:
	rm -rf $(PKGDIR)
	rm -f $(PKGNAME)_$(VERSION)*

copy: clean
	mkdir $(PKGDIR)
	cp -t $(PKGDIR)/ $(GITDIR)/CHANGELOG.md $(GITDIR)/VERSION $(GITDIR)/requirements.txt
	cp -r $(GITDIR)/sample $(PKGDIR)/
	cp -r $(GITDIR)/src $(PKGDIR)/
	find $(PKGDIR)/src | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

tarball: copy
	tar -czvf $(PKGNAME)_$(VERSION).orig.tar.gz $(PKGDIR)

debian: tarball
	cp -r debian $(PKGDIR)/
	cp -r scripts $(PKGDIR)/
	cd $(PKGDIR) && debuild -us -uc
