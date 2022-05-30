# In order to run manage.py 
# change the static files in /staticfiles DO NOT TOUCH /static
export PYTHONPATH=$PYTHONPATH:/home/ubuntu/lasair4/webserver/lasair

# when you change the static files do
python3 manage.py collectstatic

# etcapache2.tar is a sketch of the files to be added to /etc/apache2 
# to enable https proxy to 8080. Usage
# cp etcapache2.tar /etc/apache2
# cd /etc/apache2
# tar xvf etcapache2.tar
