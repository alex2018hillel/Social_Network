# Social Network
blog (REST API)
# Install
* install requirements.txt
* pip install flask_restful
* pip install passlib
* pip install Flask-WTF

# Basic Features:
* user signup

![Alt text](static/doc/post.png?raw=true "Basic Features")
![Alt text](static/doc/1.png?raw=true "Basic Features")
![Alt text](static/doc/1_2.png?raw=true "Basic Features")
* user login

![Alt text](static/doc/post.png?raw=true "Basic Features")
![Alt text](static/doc/1.png?raw=true "Basic Features")
![Alt text](static/doc/2_2.png?raw=true "Basic Features")
* post creation

![Alt text](static/doc/post.png?raw=true "Basic Features")
![Alt text](static/doc/3_1.png?raw=true "Basic Features")
![Alt text](static/doc/3_2.png?raw=true "Basic Features")
* post like

![Alt text](static/doc/post.png?raw=true "Basic Features")
![Alt text](static/doc/4_1.png?raw=true "Basic Features")
![Alt text](static/doc/4_2.png?raw=true "Basic Features")
* post unlike

* analytics about how many likes was made. 
 Example ```url /api/analitics/?date_from=2020-06-02&date_to=2020-06-15```
 API should return analytics aggregated by day.
 
 ![Alt text](static/doc/get.png?raw=true "Basic Features")
 ![Alt text](static/doc/6.png?raw=true "Basic Features")
* user activity an endpoint which will show when user was login last time and when he mades a last 
request to the service.


