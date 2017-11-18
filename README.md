# Udacity Item Catalog Project
The item catalog project is a web application that allows users to view items in a catalog based on item categories.  If the user is logged in, they can also add, edit, or delete items that they create in the application.


## How to install

1. Start by installing Python 2 to your system.  For the latest version, please visit the [Python website](https://www.python.org/).

2. Install a command line tool such as [Git BASH](https://git-for-windows.github.io/).

3. A virtual machine (VM) must also be installed to run the web server.  For this project, Vagrant and VirtualBox were used.
Files can be found from the links below:
    * https://www.virtualbox.org/wiki/Downloads
    * https://www.vagrantup.com/downloads.html 

4. Configure the the VM using files that can be found in the below link:
    - https://github.com/udacity/fullstack-nanodegree-vm

5. Download the files from this Git repository and place them into the same folder.  Make sure the files are in the same path as the virtual machine files.
    * catalogproject.py
    * database_setup.py
    * loaditems.py
    * static folder (and all it's contents)
    * templates folder (and all it's contents)

## How to setup the web server
Follow the below instructions to set up the web server.
1. Run the command line tool, such as Git Bash.
2. Start your virtual machine.  If using Vagrant, this is usually done by using the `vagrant up` command followed by `vagrant ssh`.
3. Navigate to the directory that contains the "catalogproject.py" file.
4. Using Python, run the file, "database_setup.py".  For example, `python database_setup.py`.  This will set up an sqlite database, "cataloginfo.db".
5. Next, run the file "loaditems.py".  For example, `python loaditems.py`.  This will initially populate the database with information.
6. To start the web server, run the item catalog file "catalogproject.py".  For example `python catalogproject.py`.  This will start the web server on local host 8000.
7. Finally, open a browser and type the address into the browser. `localhost:8000`

## How to use the item catalog web app
The item catalog allows you to browse a set of categories and thier items.  It also displays the 10 most recent items added to the application.
In order to add an item to the catalog, you must have a google account to sign in.  Once signed in, you can create, edit, or delete items that you have added to the application.

To view API endpoints, the addresses are as follows:
   * `/catalog/JSON`
   * `/catalog/(_category name_)/JSON`
   * `/catalog/(_categoryname_)/(_item name_)/JSON`
