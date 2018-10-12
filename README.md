# petsback
### Ulster University Computing Science COM668 (Final Year Project)

For my final year project I have created a web app with a Python and Flask back-end that is deployed via [Heroku](https://heroku.com). Heroku serves the files stored within the web/ folder that acts as the root for heroku deployment. Changes can then be pushed to Heroku using:
```
git subtree push --prefix web heroku master
```

This sends only the information to Heroku that is needed for the web app. iOS and swift files will not be included.

An iOS app has been created alongside the web app so that users can download the app to their phone, making it easier than ever to report a pet and receive notifications in real-time.
