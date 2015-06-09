POFILES=$(wildcard *.po)
LANGUAGES=en cs

all: %.pot

po: %.po

copy: %.mo
	@echo "****************"
	@echo "Copy files to locale directories"
	@for lang in $(LANGUAGES); do \
		echo "Language: $$lang"; \
		for module in $(wildcard *.mdf); do \
			install -d ../locale/$$lang/LC_MESSAGES/; \
			install -m 0644 $$lang/$${module%.*}.mo ../src/locale/$$lang/LC_MESSAGES/$${module%.*}.mo; \
		done ; \
	done ;

%pot: 
	@echo "Rebuilding the pot files"
	rm -f *.pot
	@for module in $(wildcard *.mdf); do \
		echo "module: $${module%.*}"; \
		/usr/bin/pygettext -d $${module%.*} `cat $${module}` ; \
	done ;

%.mo: %.po
	@echo "****************"
	@echo "Build mo files"
	@for lang in $(LANGUAGES); do \
		echo "Language: $$lang"; \
		for module in $(wildcard *.mdf); do \
			msgfmt --verbose -o $$lang/$${module%.*}.mo $$lang/$${module%.*}.po; \
		done ; \
	done ;

%.po: %.pot
	@echo "****************"
	@echo "Merging po files"
	@for lang in $(LANGUAGES); do \
		echo "Language: $$lang"; \
		test -d $$lang || mkdir $$lang; \
		for module in $(wildcard *.mdf); do \
			echo "module: $${module%.*}"; \
			test -f $$lang/$${module%.*}.po || touch $$lang/$${module%.*}.po; \
			msgmerge $$lang/$${module%.*}.po $${module%.*}.pot -o $$lang/$${module%.*}.po.new; \
			if [ "`diff $$lang/$${module%.*}.po $$lang/$${module%.*}.po.new | grep '[<>]' | wc -l`" -ne 2 ]; then \
				mv -f $$lang/$${module%.*}.po.new $$lang/$${module%.*}.po; \
			else \
				rm -f $$lang/$${module%.*}.po.new; \
			fi; \
			msgfmt --statistics $$lang/$${module%.*}.po; \
		done ; \
	done ;

clean:
	@for lang in $(LANGUAGES); do \
		@for module in $(wildcard *.mdf); do \
			rm -f $$lang/$${module%.*}.po; \
		done ; \
	done ;
