# In order to run manage.py 
# change the static files in /staticfiles DO NOT TOUCH /static
export PYTHONPATH=$PYTHONPATH:/home/ubuntu/lasair-new/webserver/lasair

# when you change the static files do
python3 manage.py collectstatic
