#For full instructions see
#https://lsst-uk.atlassian.net/wiki/spaces/LUSC/pages/2888663041/Feature+Set+Evolution+for+Lasair

mkdir csvfiles
python3 runner.py  --nprocess=2       --sjd=0 --ejd=2459260 --out=csvfiles
python3 runner.py  --nprocess=2 --sjd=2459260 --ejd=2459500 --out=csvfiles
python3 runner.py  --nprocess=2 --sjd=2459500 --ejd=2459600 --out=csvfiles

python3 csv_to_database.py         csvfiles
