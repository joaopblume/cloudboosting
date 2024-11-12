# Install apache2 and setup mod_wsgi apache's plugin 

## SO Version
$ cat /etc/*release
DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=24.04
DISTRIB_CODENAME=noble
DISTRIB_DESCRIPTION="Ubuntu 24.04.1 LTS"
PRETTY_NAME="Ubuntu 24.04.1 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
VERSION="24.04.1 LTS (Noble Numbat)"
VERSION_CODENAME=noble
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=noble
LOGO=ubuntu-logo
$
## Install apache2
sudo apt install apache2
sudo apt install apache2-dev
sudo apt install python3-dev

## Install mod_wsgi
wget https://files.pythonhosted.org/packages/e9/02/36597a3e2478e20ec55432dd153fd23067d2dc5ec736ae16ccc08905f8cb/mod_wsgi-5.0.1.tar.gz
tar -xvf mod_wsgi-5.0.1.tar.gz
cd mod_wsgi-5.0.1
export PYTHON_PATH=/usr/bin/python3
./configure
make
make install

chmod 644 /usr/lib/apache2/modules/mod_wsgi.so

Libraries have been installed in:
   /usr/lib/apache2/modules

vi /etc/apache2/mods-available/wsgi.load
-- colar
LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so

sudo a2enmod wsgi

sudo systemctl restart apache2

apache2ctl -M | grep wsgi

## Install Django
python -m pip install Django djangorestframework django-cors-headers

cd cloudb
django-admin startproject api_root .
python3 manage.py startapp api_rest
python3 manapy.py runserv

python manage.py migrate


python manage.py makemigrations api_rest
python manage.py migrate