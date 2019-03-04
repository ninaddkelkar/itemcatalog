Catalog
This is a web application that allows to browse through different sports categories and displays the sport gear for different sports categories. The web app allows to register new users and new users are allowed to add new sportgear linked to different sport categories.


Prerequisites
To start on this project, you'll need to have python installed on your virtual machine

The virtual machine
You can run this project on virtual machine or local machine

If you are using Virtual machine, to bring the virtual machine back online (with vagrant up), do so now. 
Then log into it with vagrant ssh.

 

Getting started :
Unzip the folder catalog.zip in your vagrant folder of your local machine. 
Go inside the folder --> cd catalog

Execute this program to set up database in your local machine  --> python database_set.py. This script will create database tables in sql lite db of your system. productcatalog.db will get created in the folder, which will be datastore for the information of this application

Execute this program to insert dummy data for your web app --> python lotofmenu.py. This script will insert data  in sql lite db of your system, thereby creating different sport categories and their respective sport gears. 

Execute this program to start the application --> python finalproject.py. This will start the web app on post 5000. 

Open the browser. Clear the historyand browser cache . Run the application on http://localhost:5000/

Now user will be able to browse. It will be allowed to register itself and edit/delete the different sport gears of the application.


Author
Ninad Kelkar