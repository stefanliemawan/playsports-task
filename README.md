# playsports-task

# How to run

Create a virtual environment and install all the dependencies from requirements.txt using your preferred package manager.

Then, simply run `run_app.bat` (for Windows environment) or `run_app.sh`(for Linux environment) to start the server in localhost

All the possible routes are as follows:

```
POST http://localhost:5000/videos/ HTTP/1.1 (with empty body)

GET http://localhost:5000/videos HTTP/1.1

GET http://localhost:5000/videos?q=<query> HTTP/1.1

GET http://localhost:5000/videos/<id> HTTP/1.1

DELETE http://localhost:5000/videos/<id> HTTP/1.1
```
