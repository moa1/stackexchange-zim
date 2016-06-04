# this config file must be interpretable as both a python source file and a Makefile.

# the domain of the stackexchange site
#stackexchange_domain=["cs.stackexchange.com","meta.beer.stackexchange.com"]
stackexchange_domain="superuser.com"
# the packed 7z file containing the xml files of the stackexchange site, or, for the site stackoverflow.com, the path to the stackoverflow 7z files, truncated after the "-", e.g. "/tmp/superuser.com.7z-"
stackexchange_dump="/home/itoni/Downloads/stackexchange-dump-20160301/superuser.com.7z"
#stackexchange_dump="/home/itoni/Downloads/stackexchange-dump-20160301/stackoverflow.com-"
# the path of a temporary directory with lots of free space
tempdir="temp"
# title that the zim file should have
zim_title="stackexchange dump"
# the Sites.xml file of the stackexchange dump listing all stackexchange sites. set this to "" if the file is not available
sites_xml="/home/itoni/Downloads/stackexchange-dump-20160301/Sites.xml"
