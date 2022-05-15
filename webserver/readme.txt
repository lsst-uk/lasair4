# In order to run manage.py 
# change the static files in /staticfiles DO NOT TOUCH /static
export PYTHONPATH=$PYTHONPATH:/home/ubuntu/lasair4/webserver/lasair

# when you change the static files do
python3 manage.py collectstatic
