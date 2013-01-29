
PYTHON=./venv/bin/python
if [ ! -x $PYTHON  ]; then
  PYTHON=python
fi
DB_FILE=var/www/db.sqlite
if [ -e /var/webdemo ]; then
  DB_FILE=/var/webdemo/db.sqlite
fi

echo "PYTHON=$PYTHON"
echo "DB_FILE=$DB_FILE"

sudo /etc/init.d/apache2 stop
sudo rm $DB_FILE
sudo $PYTHON manage.py syncdb
sudo $PYTHON manage.py createcachetable cache_table
sudo chown www-data:www-data $DB_FILE
sudo /etc/init.d/apache2 start

