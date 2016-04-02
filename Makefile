include config.py

zim_description="Questions and answer site http://${stackexchange_domain}"
zim_author="Users of http://$(stackexchange_domain) and Stackexchange"

.PHONY: clean

all: temp/stackexchange-dump.zim

temp: temp/created
temp/created:
	mkdir -p temp
	touch temp/created

database: temp/finished-database
temp/finished-database: temp/created
	python createtables.py
	python filltables.py
	python fillPostsTagstable.py
	touch temp/finished-database

content: temp/finished-content
temp/finished-content: temp/finished-database
	mkdir -p temp/content
	mkdir "temp/content/$(stackexchange_domain)"
	ln -f -s ../../../favicon.png temp/content/$(stackexchange_domain)/
	ln -f -s ../../../se.css temp/content/$(stackexchange_domain)/
	python badges.py
	python users.py
	python questions.py
	python tags.py
	python indices.py
	touch temp/finished-content

temp/content/index.html: temp/finished-content
	ln -f -s ../../favicon.png temp/content/
	ln -f -s ../../se.css temp/content/
	@echo "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /><title>Index of the stackexchange.com dump</title><link href=\"se.css\" rel=\"stylesheet\" type=\"text/css\"></head><body><p><h1><a class=\"internallink\" href=\"$(stackexchange_domain)/index.html\">$(stackexchange_domain) dump</a></h1></p></body></html>" > temp/content/index.html

zim: temp/stackexchange-dump.zim
temp/stackexchange-dump.zim: temp/finished-content temp/content/index.html
	./zimwriterfs -w index.html -f favicon.png -l eng -t $(zim_title) -d $(zim_description) -c $(zim_author) -p "maksezim" temp/content/ temp/stackexchange-dump.zim

squashfs: temp/stackexchange-dump.squashfs
temp/stackexchange-dump.squashfs: temp/finished-content
	mksquashfs temp/content/ temp/stackexchange-dump.squashfs -comp xz -no-xattrs -all-root

clean:
	rm -rf temp
