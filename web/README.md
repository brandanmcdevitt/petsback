# petsback

### Web App for COM668 (Final Year Project)

Push subtree for Heroku root within petsback/web. This way iOS and other uneeded folders don't get pushed to Heroku's remote.
```
git subtree push --prefix web heroku master
```

Run the Web App locally with Heroku:
```
heroku local
```

Check the logs to determine errors:
```
heroku logs --tail
```
