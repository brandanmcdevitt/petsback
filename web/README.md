# PetsBack.me

#### Web App for COM668 (Final Year Project)

Push subtree for Heroku root within PetsBack.Project/web. This way iOS and other uneeded folders don't get pushed to Heroku's remote.
```
git subtree push --prefix web heroku master
```

Run the Web App locally with flask:
```
export FLASK_APP=application.py
flask run
```

Check the logs to determine errors:
```
heroku logs --tail
```

SQLAlchemy database query:
```
db.session.query(User.username).all()
User.query.filter(User.username == username).first()
```