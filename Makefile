.PHONY: all temp database content clean

all: content

temp:
	mkdir temp

database: temp
	python createtables.py
	python filltables.py
	python fillPostsTagstable.py

content: database
	mkdir temp/content
	ln -s ../../favicon.png temp/content/
	ln -s ../../se.css temp/content/
	python users.py
	python posts.py
	python tags.py
	python indices.py

clean:
	rm -rf temp
