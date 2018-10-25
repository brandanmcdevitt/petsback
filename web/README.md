# petsback

### Web App for COM668 (Final Year Project)

Push subtree for Heroku root within petsback/web. This way iOS and other uneeded folders don't get pushed to Heroku's remote.
```
git subtree push --prefix web heroku master
```

Create a backup of the database and download it
```
heroku pg:backups:capture
heroku pg:backups:download
```

Push backup to local db for local development
```
pg_restore --verbose --clean --no-acl --no-owner -h localhost -U brandanmcdevitt -d petsback latest.dump
```

Run the Web App locally with Heroku:
```
heroku local
```

Check the logs to determine errors:
```
heroku logs --tail
```

Create the database:
```
from app import db
db.create_all()
```

Example SQLAlchemy database query:
```
db.session.query(User.username).all()
User.query.filter(User.username == username).first()
```
