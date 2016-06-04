include config.py

# remove quotes
stackexchange_domain := $(patsubst "%",%,$(stackexchange_domain))
zim_description="Questions and answer site http://${stackexchange_domain}"
zim_author="Users of http://$(stackexchange_domain) and Stackexchange"
stackexchange_dump := $(patsubst "%",%,$(stackexchange_dump))

.PHONY: clean

all: temp/stackexchange-dump.zim

all-stackoverflow: database-stackoverflow temp/stackexchange-dump.zim

temp: temp/created
temp/created:
	mkdir -p temp
	touch temp/created

database: temp/finished-database
temp/finished-database: temp/created
	p7zip -k -c -d "$(stackexchange_dump)" | python remove-head.py  | python createtables.py
	python createindices.py
	p7zip -k -c -d "$(stackexchange_dump)" | python remove-head.py  | python filltables.py
	python fillPostsTagstable.py
	touch temp/finished-database

database-stackoverflow: temp/finished-database-stackoverflow
temp/finished-database-stackoverflow: temp/created
	p7zip -k -c -d "$(stackexchange_dump)Tags.7z" | python remove-head.py  | python createtables.py
	p7zip -k -c -d "$(stackexchange_dump)Badges.7z" | python remove-head.py  | python createtables.py
	p7zip -k -c -d "$(stackexchange_dump)Comments.7z" | python remove-head.py  | python createtables.py
	p7zip -k -c -d "$(stackexchange_dump)Posts.7z" | python remove-head.py  | python createtables.py
	p7zip -k -c -d "$(stackexchange_dump)Users.7z" | python remove-head.py  | python createtables.py
	python createindices.py
	p7zip -k -c -d "$(stackexchange_dump)Tags.7z" | python remove-head.py  | python filltables.py
	p7zip -k -c -d "$(stackexchange_dump)Badges.7z" | python remove-head.py  | python filltables.py
	p7zip -k -c -d "$(stackexchange_dump)Comments.7z" | python remove-head.py  | python filltables.py
	p7zip -k -c -d "$(stackexchange_dump)Posts.7z" | python remove-head.py  | python filltables.py
	p7zip -k -c -d "$(stackexchange_dump)Users.7z" | python remove-head.py  | python filltables.py
	python fillPostsTagstable.py
	touch temp/finished-database

temp/content/index.html:
	mkdir -p "temp/content"
	ln -f -s ../../favicon.png temp/content/
	ln -f -s ../../se.css temp/content/
	@echo "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /><title>Index of the stackexchange.com dump</title><link href=\"se.css\" rel=\"stylesheet\" type=\"text/css\"></head><body><p><h1><a class=\"internallink\" href=\"$(stackexchange_domain)/index.html\">$(stackexchange_domain) dump</a></h1></p></body></html>" > temp/content/index.html

content: temp/finished-content
temp/finished-content: temp/finished-database temp/content/index.html
	mkdir -p "temp/content/$(stackexchange_domain)"
	mkdir -p "temp/content/$(stackexchange_domain)/tag"
	mkdir -p "temp/content/$(stackexchange_domain)/question"
	mkdir -p "temp/content/$(stackexchange_domain)/user"
	mkdir -p "temp/content/$(stackexchange_domain)/badge"
	ln -f -s ../../../favicon.png temp/content/$(stackexchange_domain)/
	ln -f -s ../../../se.css temp/content/$(stackexchange_domain)/
	python indices.py
	python tags.py
	python questions.py
	python users.py
	python badges.py
	touch temp/finished-content

zim: temp/stackexchange-dump.zim
temp/stackexchange-dump.zim: temp/finished-content
	./zimwriterfs -w index.html -f favicon.png -l eng -t $(zim_title) -d $(zim_description) -c $(zim_author) -p "maksezim" temp/content/ temp/stackexchange-dump.zim

squashfs: temp/stackexchange-dump.squashfs
temp/stackexchange-dump.squashfs: temp/finished-content
	mksquashfs temp/content/ temp/stackexchange-dump.squashfs -comp xz -no-xattrs -all-root

clean:
	rm -rf temp
