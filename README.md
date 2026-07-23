# it-risk-manager-v2
More complex version of my ITRM application: now integranted into a locally hosted, client-server architecture designed to run within a container. Same CRUD functionalities, now with a web interface.
Feel free to modify the project to adjust to your own needs, ITRM was an academic project of mine to practice fullstack development.

# Quick setup on Docker

Importing the image...
`docker load -i itrmv2.tar itrmv2`

Running the container...
`docker run -d -p 5023:5000 -v "$(pwd)/data:/itrm/data" --name itrmv2 itrmv2`

Port `5023` can be changed to whatever you want or to what's available in your machine.
Access the application through `localhost:5023` in your browser if you are running it locally.
The volume created in `-v "$(pwd)/data:/itrm/data"` is important to assure the persistance of the database file throughout restarts.
