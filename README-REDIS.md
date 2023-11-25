# Using redis

## Pull the latest Redis Docker image (v6.2.2 at the time of writing)

This is like downloading the installation file for Redis.

`docker pull redis`

## Run the Redis server as a daemon (background process)

In this command, we map port 6379 on our computer to the exposed port 6379 from the Redis container. Port 6379 is the default port for Redis servers.

`docker run -d -p 6379:6379 --name redis-server redis`

## Connect to the Redis server

The Redis server we started in the previous section has a Redis CLI client built into it. We’ll use that for this part of the tutorial.

`docker exec -it redis-server redis-cli`


## Resources

1. https://betterprogramming.pub/getting-started-with-redis-a-python-tutorial-3a18531a73a6
1. https://realpython.com/python-redis/
