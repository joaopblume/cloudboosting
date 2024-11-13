# Install apache2 and setup mod_wsgi apache's plugin 
```markdown
## Prerequisites

Before you begin, ensure you have the following:

- A running instance of Ubuntu 24.04.1 LTS
- Sudo privileges

## Step 1: Update System Packages

Update your system packages to the latest version:

```sh
sudo apt update
sudo apt upgrade
```

## Step 2: Install Apache2

Install Apache2 and its development package:

```sh
sudo apt install apache2
sudo apt install apache2-dev
```

## Step 3: Install Python Development Package

Install the Python development package:

```sh
sudo apt install python3-dev
```

## Step 4: Install mod_wsgi

Download and install mod_wsgi:

```sh
wget https://files.pythonhosted.org/packages/e9/02/36597a3e2478e20ec55432dd153fd23067d2dc5ec736ae16ccc08905f8cb/mod_wsgi-5.0.1.tar.gz
tar -xvf mod_wsgi-5.0.1.tar.gz
cd mod_wsgi-5.0.1
export PYTHON_PATH=/usr/bin/python3
./configure
make
sudo make install
```

Set the correct permissions for the mod_wsgi module:

```sh
sudo chmod 644 /usr/lib/apache2/modules/mod_wsgi.so
```

## Step 5: Configure Apache to Use mod_wsgi

Create the `wsgi.load` file:

```sh
sudo vi /etc/apache2/mods-available/wsgi.load
```

Add the following line to the file:

```sh
LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so
```

Enable the `wsgi` module and restart Apache:

```sh
sudo a2enmod wsgi
sudo systemctl restart apache2
```

Verify that the `wsgi` module is enabled:

```sh
apache2ctl -M | grep wsgi
```

## Step 6: Install Django

Install Django and related packages:

```sh
python -m pip install Django djangorestframework django-cors-headers
```

## Step 7: Set Up Django Project

Navigate to your project directory and set up a new Django project:

```sh
cd cloudb
django-admin startproject api_root .
python3 manage.py startapp api_rest
python3 manage.py runserver
```

## Step 8: Apply Migrations

Apply the initial migrations for your Django app:

```sh
python manage.py makemigrations api_rest
python manage.py migrate
```

## Step 9: Create a Superuser

Create a superuser for your Django admin:

```sh
python manage.py createsuperuser
```

Follow the prompts to set the username and password for the superuser.
```
