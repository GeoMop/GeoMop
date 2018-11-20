# target which runs "test" on jenkins-jobs

geomop.ini:
	@echo "Copy 'geomop.ini.template' to 'geomop.ini'"
	@echo "and set your username and password there."


test: 
	jenkins-jobs test geomop.yaml


.PHONY: geomop.ini
upload: 
	jenkins-jobs --conf geomop.ini --ignore-cache update geomop.yaml
	