cd /data/server/br13_IPLocator/doc
python qqwry.py --dump -o ip.txt
cd /data/server/br13_IPLocator
python main_createdb.py --in=doc/ip.txt --out=doc/ip_clean.world.txt --group=doc/country.world.txt
python main_createdb.py --in=doc/ip.txt --out=doc/ip_clean.china.txt --group=doc/country.china.txt
