GITDIR=..
PKGNAME=geomop

VERSION=$(shell python update_version.py)

PKGDIR=$(PKGNAME)-${VERSION}

PKGMESAMPLEDIR=$(PKGDIR)/sample/ModelEditor
GITMESAMPLEDIR=$(GITDIR)/sample/ModelEditor

clean: version
	rm -rf $(PKGNAME)-*
	rm -f $(PKGNAME)*

copy: clean
	mkdir $(PKGDIR)
	cp -t $(PKGDIR)/ $(GITDIR)/changes.md $(GITDIR)/version.yml $(GITDIR)/requirements.txt
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
		cp -r $(GITDIR)/submodules/yaml_converter $(PKGDIR)/src
	find $(PKGDIR)/src | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

orig: copy
	cp -r $(PKGDIR) $(PKGDIR).orig
	#tar -czvf $(PKGNAME)_$$VERSION.orig.tar.gz $(PKGDIR)

debian: orig
	cp -r debian $(PKGDIR)/
	cp -r scripts $(PKGDIR)/
	cd $(PKGDIR) && debuild -us -uc
	mv *.deb $(GITDIR)/dist

version:
	#echo $(VERSION)
	#cat debian/control_template | sed "1s/.*/Version: $(VERSION)/" > debian/control
	echo "geomop ($(VERSION)) UNRELEASED; urgency=medium" > debian/changelog
	echo "\n  * Release." >> debian/changelog
	echo "\n -- Jan Březina <jan.brezina@tul.cz>  $$(date -R)" >> debian/changelog

