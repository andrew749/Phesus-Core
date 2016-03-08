# Phesus-Core
Core is the main application for phesus, handling user interaction.
## Setup
### First install postgresql on your computer.
```
brew install postgresql
OR
sudo apt-get install postgresql
```
### Create a database called phesus.
```
createdb phesus
```

### Create a new user called dummy.

```
createuser -w dummy
```
### Add google client id and secret to app.py

### Create a virtualenv for the project
```
virtualenv -p /usr/local/bin/python3.5 .
```
### Run the virtualenv
```
. bin/activate
```
### Install dependencies
```
pip install -r requirements.txt
```

##Running the server
```
. bin/activate
.Core/app.py
```

