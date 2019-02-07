# ghcfd
Scripts to auto-generate a Kanban cumulative flow diagram for your Github project board, and a CFD for your all your opened and closed issues on a weekly timeline.

For the Kanban CFD, the gh_kanban_cfd.py script assumes that you have the following lists created on your Github project Kanban board:

```To Do | In Progress | Verify | Done```

The CFD will be generated for these columns only. The file.csv should reside in the same location as the python script and should have the following at the top before script is executed:

```Date,To Do,In Progress,Verify,Done```

The CFD is generated using matplotlib. Other requirements are numpy and PyGithub for accessing your Github repository. Make sure to enter your username, password, and Github repository in the script before executing.

Label based filtering can also be done which would allow generation of separate reports for each Github label. This is particularly helpful when issues are separate by functional domains (for example, Server, Client, Android, etc.). The labels can be added as strings to the LABEL_FILTER list in the script.

---

To generate the CFD for the opened and closed issues in your repository, the gh_issues_cfd.py script should be used. Similar to the Kanban CFD, make sure to enter your credentials before using the script. You can use the Github token instead of your login credentials by retrieving it from your Github Settings.

The issues CFD will generate a local dump the first time as 'issues_dump'. This helps in speeding up generation of the plot in subsequent script runs. However, you would need to delete the issues_dump file to get the latest status on your project.

