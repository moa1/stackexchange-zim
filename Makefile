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
	./p7zip -k -c -d "$(stackexchange_dump)" | python remove-head.py  | python createtables.py
	python createindices.py
	./p7zip -k -c -d "$(stackexchange_dump)" | python remove-head.py  | python filltables.py
	python fillPostsTagstable.py
	touch temp/finished-database

database-stackoverflow: temp/finished-database-stackoverflow
temp/finished-database-stackoverflow: temp/created
	./p7zip -k -c -d "$(stackexchange_dump)Tags.7z" | python createtables.py
	./p7zip -k -c -d "$(stackexchange_dump)Badges.7z" | python createtables.py
	./p7zip -k -c -d "$(stackexchange_dump)Comments.7z" | python createtables.py
	./p7zip -k -c -d "$(stackexchange_dump)Posts.7z" | python createtables.py
	./p7zip -k -c -d "$(stackexchange_dump)Users.7z" | python createtables.py
	python createindices.py
	./p7zip -k -c -d "$(stackexchange_dump)Tags.7z" | python filltables.py
	./p7zip -k -c -d "$(stackexchange_dump)Badges.7z" | python filltables.py
	./p7zip -k -c -d "$(stackexchange_dump)Comments.7z" | python filltables.py
	./p7zip -k -c -d "$(stackexchange_dump)Posts.7z" | python filltables.py
	./p7zip -k -c -d "$(stackexchange_dump)Users.7z" | python filltables.py
	python fillPostsTagstable.py
	touch temp/finished-database


#rest: temp/created
#	./p7zip -k -c -d "$(stackexchange_dump)Posts.7z" | python filltables.py
#	./p7zip -k -c -d "$(stackexchange_dump)Users.7z" | python remove-head.py  | python filltables.py
#	python fillPostsTagstable.py
#	touch temp/finished-database

#head.txt: (containing an <U+FEFF> UTF-8 character at position 0)
#<?xml version="1.0" encoding="utf-8"?>
#<posts>

#tail.txt:
#</posts>

rest1: temp/created
# a line-break offset is at 2500001589, so if I start at 52, I have to "count=$((2500001589-52))".
	dd if=/mnt/platte/tmp/stackoverflow.com/Posts.xml iflag=skip_bytes,count_bytes skip=52 count=2500001537 | cat /mnt/platte/tmp/stackoverflow.com/head.txt - /mnt/platte/tmp/stackoverflow.com/tail.txt | python filltables.py

rest2: temp/created
# a line-break offset is at 6000000273, so if I start at 2500001589, I have to "count=$((6000000273-2500001589))".
	dd if=/mnt/platte/tmp/stackoverflow.com/Posts.xml iflag=skip_bytes,count_bytes skip=2500001589 count=3499998684 | cat /mnt/platte/tmp/stackoverflow.com/head.txt - /mnt/platte/tmp/stackoverflow.com/tail.txt | python filltables.py

rest3: temp/created
# a line-break offset is at 15000000537, so if I start at 6000000273, I have to "count=$((15000000537-6000000273))".
	dd if=/mnt/platte/tmp/stackoverflow.com/Posts.xml iflag=skip_bytes,count_bytes skip=6000000273 count=9000000264 | cat /mnt/platte/tmp/stackoverflow.com/head.txt - /mnt/platte/tmp/stackoverflow.com/tail.txt | python filltables.py

rest4: temp/created
# a line-break offset is at 23000000674, so if I start at 15000000537, I have to "count=$((23000000674-15000000537))".
	dd if=/mnt/platte/tmp/stackoverflow.com/Posts.xml iflag=skip_bytes,count_bytes skip=15000000537 count=8000000137 | cat /mnt/platte/tmp/stackoverflow.com/head.txt - /mnt/platte/tmp/stackoverflow.com/tail.txt | python filltables.py

rest5: temp/created
# a line-break offset is at 28000000325, so if I start at 23000000674, I have to "count=$((28000000325-23000000674))".
	dd if=/mnt/platte/tmp/stackoverflow.com/Posts.xml iflag=skip_bytes,count_bytes skip=23000000674 count=4999999651 | cat /mnt/platte/tmp/stackoverflow.com/head.txt - /mnt/platte/tmp/stackoverflow.com/tail.txt | python filltables.py

rest6: temp/created
# a line-break offset is at skip=33000000130, so if I start at 28000000325, I have to "count=$((skip=33000000130-28000000325))".
	dd if=/mnt/platte/tmp/stackoverflow.com/Posts.xml iflag=skip_bytes,count_bytes skip=28000000325 count=4999999805 | cat /mnt/platte/tmp/stackoverflow.com/head.txt - /mnt/platte/tmp/stackoverflow.com/tail.txt | python filltables.py

rest7: temp/created
# a line-break offset is at skip=38000000916, so if I start at 33000000130, I have to "count=$((skip=38000000916-33000000130))".
	dd if=/mnt/platte/tmp/stackoverflow.com/Posts.xml iflag=skip_bytes,count_bytes skip=33000000130 count=5000000786 | cat /mnt/platte/tmp/stackoverflow.com/head.txt - /mnt/platte/tmp/stackoverflow.com/tail.txt | python filltables.py

rest8: temp/created
# a line-break offset is at skip=43000002385, so if I start at 38000000916, I have to "count=$((skip=43000002385-38000000916))".
	dd if=/mnt/platte/tmp/stackoverflow.com/Posts.xml iflag=skip_bytes,count_bytes skip=38000000916 count=5000001469 | cat /mnt/platte/tmp/stackoverflow.com/head.txt - /mnt/platte/tmp/stackoverflow.com/tail.txt | python filltables.py

rest9: temp/created
# a line-break offset is at skip=43000002385, so if I start at 38000000916, I have to "count=$((skip=43000002385-38000000916))".
	dd if=/mnt/platte/tmp/stackoverflow.com/Posts.xml iflag=skip_bytes,count_bytes skip=43000002385 | cat /mnt/platte/tmp/stackoverflow.com/head.txt - | python filltables.py

rest10: temp/created
	cat /mnt/platte/tmp/stackoverflow.com/Users.xml | python filltables.py
	python fillPostsTagstable.py
	touch temp/finished-database

temp/content/index.html:
	mkdir -p "temp/content"
	#ln -f -s ../../favicon.png temp/content/
	#ln -f -s ../../se.css temp/content/
	cp favicon.png temp/content/
	cp se.css temp/content/
	@echo "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /><title>Index of the stackexchange.com dump</title><link href=\"se.css\" rel=\"stylesheet\" type=\"text/css\"></head><body><p><h1><a class=\"internallink\" href=\"$(stackexchange_domain)/index.html\">$(stackexchange_domain) dump</a></h1></p></body></html>" > temp/content/index.html

content: temp/finished-content
temp/finished-content: temp/finished-database temp/content/index.html
	mkdir -p "temp/content/$(stackexchange_domain)"
	mkdir -p "temp/content/$(stackexchange_domain)/tag"
	mkdir -p "temp/content/$(stackexchange_domain)/question"
	mkdir -p "temp/content/$(stackexchange_domain)/user"
	mkdir -p "temp/content/$(stackexchange_domain)/badge"
	ln -f -s ../favicon.png "temp/content/$(stackexchange_domain)/"
	ln -f -s ../se.css "temp/content/$(stackexchange_domain)/"
	#cp favicon.png "temp/content/$(stackexchange_domain)/"
	#cp se.css "temp/content/$(stackexchange_domain)/"
	python indices.py
	python tags.py
	python questions.py
	python users.py
	python badges.py
	touch temp/finished-content

zim: temp/stackexchange-dump.zim
temp/stackexchange-dump.zim: temp/finished-content
	echo $(zim_title)
	./zimwriterfs -v -w index.html -f favicon.png -l eng -t $(zim_title) -d $(zim_description) -c $(zim_author) -p "maksezim" temp/content/ temp/stackexchange-dump.zim

# $ make zim
# ...
# Creating entry for stackoverflow.com/question/8898042.html
# Creating entry for stackoverflow.com/question/8665813.html
# Creating entry for stackoverflow.com/question/4430204.html
# Creating entry for stackoverflow.com/question/35273218.html
# Creating entry for stackoverflow.com/question/23737215.html
# Creating entry for stackoverflow.com/question/274418.html
# Creating entry for stackoverflow.com/question/2656157.html
# Creating entry for stackoverflow.com/question/31775360.html
# std::bad_alloc

squashfs: temp/stackexchange-dump.squashfs
temp/stackexchange-dump.squashfs: temp/finished-content
	mksquashfs temp/content/ temp/stackexchange-dump.squashfs -comp xz -no-xattrs -all-root

clean:
	rm -rf temp

# $ nice mksquashfs stackoverflow.com/question/ stackoverflow.com.questions.squashfs -comp xz -no-xattrs -all-root -no-duplicates
# Parallel mksquashfs: Using 2 processors
# Creating 4.0 filesystem on stackoverflow.com.questions.squashfs, block size 131072.
# [=====================================================================================================================================-] 11203257/11203257 100%
# FATAL ERROR:directory greater than 2^27-1 bytes!
# [=====================================================================================================================================\] 11203257/11203257 100
