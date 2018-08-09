# CSCI S-33a: Final Project

#### Your name

Satyanarayana Tammineedi

#### Your teaching fellow's name

David Nunez

#### Project Title
Simple Planner

#### What is the tool about?

This is a simple planning tool that enables users and teams to create plans, assemble and assign tasks and collaborate with other users

UI: Featues:
    Ability to create the Projects
    >> What is a Project? Project is group of your related Tasks, workitems.
    >> There are 2 types of Projects
    >>> Personal Project - where you are keeping track of your personal task items
    >>> Team Project - You can create task list and assign to different team members with due dates

    Ability to move tasks from one bucket(status) to another in a project
    >> To keep track of the status of your tasks you can move the tasks from one bucket to another

    Ability to add/delete Tasks in each bucket
    >> You will be able to create new task items in each bucket(status).
    >> If you are creating a tasks

    Ability to edit and re-assign Tasks in each bucket
    >> You can always update the Task detials and re-assign to different team members.

    Ability to add team members to the project
    >> You can select the users and add to your team.
    >> currently removing of users is not supported.

    Archive/Activate the Project
    >> By default when project is created it is an active project.
    >> If you would like to freeze updates, and archive the project
    >> Click on the Archive project and all edit functionality is disabled.
    >> You can always bring back the project to Active Status.

    Global Dashboard
    >> Global Dashboard provides the Stats on # of Projects and # of Tasks

Database:
    Database is desinged with additional capabilities to the application in mind
    1. You can add comments to each Task - feature not implimented
    2. Buckets can be customizable - you can change the names of buckets from django admin screen
    3. Design is provisioned to extend number of buckets to any number

