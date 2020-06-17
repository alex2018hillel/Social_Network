# Social Network
blog (REST API)
# Install
* install requirements.txt
* pip install flask_restful
* pip install passlib
* pip install Flask-WTF
* pip install psycopg2

# Basic Features:
* user signup - /api/registration  Example:
{
    "username": "test4444",
    "email": "emailX4@yahoo.com",
    "password": "testTEST4"
}

![Alt text](static/doc/post.png?raw=true "Basic Features")
![Alt text](static/doc/1.png?raw=true "Basic Features")
![Alt text](static/doc/1_2.png?raw=true "Basic Features")
* user login - /api/login  Example: POST,
{
    "username": "test4444",
    "email": "emailX4@yahoo.com",
    "password": "testTEST4"
}

![Alt text](static/doc/post.png?raw=true "Basic Features")
![Alt text](static/doc/1.png?raw=true "Basic Features")
![Alt text](static/doc/2_2.png?raw=true "Basic Features")
* post creation - /post/create  Example: POST,
{
    "content": "abcd"
}

![Alt text](static/doc/post.png?raw=true "Basic Features")
![Alt text](static/doc/3_1.png?raw=true "Basic Features")
![Alt text](static/doc/3_2.png?raw=true "Basic Features")
* post like - /api/post/like  Example: POST,
{"like": "True", "post_id":"3"}

![Alt text](static/doc/post.png?raw=true "Basic Features")
![Alt text](static/doc/4_1.png?raw=true "Basic Features")
![Alt text](static/doc/4_2.png?raw=true "Basic Features")
* post unlike  - /api/post/like  Example: POST,
{"like": "False", "post_id":"3"}

* analytics about how many likes was made - /api/analitics/
 API should return analytics aggregated by day.
 Example: GET,  /api/analitics/?date_from=2020-06-02&date_to=2020-06-15
 
 ![Alt text](static/doc/get.png?raw=true "Basic Features")
 ![Alt text](static/doc/6.png?raw=true "Basic Features")
* user activity an endpoint which will show when user was login last time and when he mades a last 
request to the service -  /api/activity/<user>
 Example: GET, /api/activity/test4444
 
