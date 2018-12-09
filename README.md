# ghcfd
A script to auto-generate a cumulative flow diagram for your Github project board.

This program assumes that you have the following lists created on your Github project Kanban board:

Backlog | To Do | In Progress | Verify | Done

The CFD will be generated for these columns only. The file.csv should reside in the same location as the python script and should have the following at the top before script is executed:

Date,Backlog,To Do,In Progress,Verify,Done

The CFD is generated using matplotlib. Other requirements are numpy and PyGithub for accessing your Github repository.

Make sure to enter your username, password, and Github repository in the script before executing.

