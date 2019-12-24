# /bin/sh

# this script installs prerequisites for arobator
# and connect it to apache2 server
# under ubuntu 16.04 / 18.04

set -x

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROGRAM=$DIR
LINK="/var/www/html/arborator"
CONFIG_FILE="/etc/apache2/sites-enabled/000-default.conf"
CGI_MODULE="/etc/apache2/mods-available/cgi.load"
ENABLED_MODULES="/etc/apache2/mods-enabled"

# ubuntu libraries & python modules & arobator
sudo apt-get install git python-pip python-nltk tasksel -y
sudo tasksel install lamp-server
sudo pip install jellyfish

# make the program folder and all .cgi files it contains writable & executable
# then link the folder of arborator-server to /var/www/html/arborator
if [ -L $LINK ]; then
	sudo bash -c "rm $LINK"
fi
sudo bash -c "ln -s $PROGRAM $LINK"
sudo bash -c "chmod -R a+rw $PROGRAM"
sudo bash -c "find $PROGRAM -name \"*.cgi\" -exec chmod +x {} \;"

# apache2 configuration
if [ -L $LINK ]; then
sudo bash -c "rm $ENABLED_MODULES/$(basename $CGI_MODULE)"
fi
sudo bash -c "ln -s $CGI_MODULE $ENABLED_MODULES"
if [ -e $CONFIG_FILE ]; then
	sudo sed -i 's/<\/VirtualHost>/<Directory \/var\/www\/html>\nOptions Indexes FollowSymLinks MultiViews\nOptions +FollowSymLinks\nOptions +ExecCGI\nAddHandler cgi-script .cgi\nAllowOverride None\nOrder allow,deny\nallow from all\n<\/directory>\n<\/VirtualHost>/g' $CONFIG_FILE
fi
sudo /etc/init.d/apache2 restart
