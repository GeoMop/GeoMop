GITDIR=..
VERSION=1.0.0b
PKGNAME=geomop

PKGDIR=$(PKGNAME)-$(VERSION)

PKGMESAMPLEDIR=$(PKGDIR)/sample/ModelEditor
GITMESAMPLEDIR=$(GITDIR)/sample/ModelEditor

clean:
	rm -rf $(PKGDIR)
	rm -f $(PKGNAME)_$(VERSION)*

copy: clean
	mkdir $(PKGDIR)
	cp -t $(PKGDIR)/ $(GITDIR)/CHANGELOG.md $(GITDIR)/VERSION $(GITDIR)/requirements.txt
	mkdir $(PKGDIR)/sample
	mkdir $(PKGMESAMPLEDIR)
	cp -r $(GITMESAMPLEDIR)/ConFiles $(PKGMESAMPLEDIR)
	mkdir $(PKGMESAMPLEDIR)/YamlFiles
	cp $(GITMESAMPLEDIR)/YamlFiles/flow_21d.yaml $(PKGMESAMPLEDIR)/YamlFiles/
	cp $(GITMESAMPLEDIR)/YamlFiles/flow_time_dep.yaml $(PKGMESAMPLEDIR)/YamlFiles/
	cp $(GITMESAMPLEDIR)/YamlFiles/flow_trans_explicit.yaml $(PKGMESAMPLEDIR)/YamlFiles/
	cp $(GITMESAMPLEDIR)/YamlFiles/flow_vtk.yaml $(PKGMESAMPLEDIR)/YamlFiles/
	cp $(GITMESAMPLEDIR)/YamlFiles/flow_vtk_source.yaml $(PKGMESAMPLEDIR)/YamlFiles/
	cp -r $(GITDIR)/src $(PKGDIR)/
	find $(PKGDIR)/src | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

tarball: copy
	tar -czvf $(PKGNAME)_$(VERSION).orig.tar.gz $(PKGDIR)

debian: tarball
	cp -r debian $(PKGDIR)/
	cp -r scripts $(PKGDIR)/
	cd $(PKGDIR) && debuild -us -uc
