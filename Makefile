.PHONY: clean

all: temp/blender.stackexchange.com.zim

temp/created:
	mkdir -p temp
	touch temp/created

temp/finished-database: temp
	python createtables.py
	python filltables.py
	python fillPostsTagstable.py
	touch temp/finished-database

temp/finished-content: temp/finished-database
	mkdir -p temp/content
	ln -f -s ../../favicon.png temp/content/
	ln -f -s ../../se.css temp/content/
	python users.py
	python posts.py
	python tags.py
	python indices.py
	touch temp/finished-content

temp/blender.stackexchange.com.zim: temp/finished-content
	./zimwriterfs -w index_posts.html -f favicon.png -l eng -t "blender.stackexchange.com" -d "Questions and answers about Blender on http://blender.stackexchange.com" -c "Users of http://blender.stackexchange.com" -p "maksezim" temp/content/ temp/blender.stackexchange.com.zim

clean:
	rm -rf temp
