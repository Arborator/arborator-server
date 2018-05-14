# /bin/sh

# this script install arobator for locally test purpose
# in ubuntu 16.04 / 18.04

# AROBATOR_REPO="https://github.com/Arborator/arborator-server"
AROBATOR_REPO="https://github.com/vieenrose/arborator-server"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROGRAM=$DIR"/arborator-server"
LINK="/var/www/html/arborator"
CONFIG_FILE="/etc/apache2/sites-enabled/000-default.conf"

# ubuntu libraries & python modules & arobator
sudo apt-get install git python-pip python-nltk tasksel -y
sudo tasksel install lamp-server
sudo pip install jellyfish
git clone $AROBATOR_REPO

# make the program folder and all .cgi files it contains writable & executable
# then link the folder of arborator-server to /var/www/html/arborator
sudo bash -c "rm $LINK"
sudo bash -c "ln -s $PROGRAM $LINK"
sudo bash -c "chmod -R a+rw $PROGRAM"
sudo bash -c "echo -e 'find $PROGRAM -name \"*.cgi\" -exec chmod +x {} \;'"

# apache2 configuration
sudo bash -c "ln -s ../mods-available/cgi.load /etc/apache2/mods-enabled"
if [ -e $CONFIG_FILE ]; then
	sudo sed -i 's/<\/VirtualHost>/<Directory \/var\/www\/html>\nOptions Indexes FollowSymLinks MultiViews\nOptions +FollowSymLinks\nOptions +ExecCGI\nAddHandler cgi-script .cgi\nAllowOverride None\nOrder allow,deny\nallow from all\n<\/directory>\n<\/VirtualHost>/g' $CONFIG_FILE
fi
sudo /etc/init.d/apache2 restart
