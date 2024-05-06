Simple demo to show how to create a write through cache with redis and psql

```
/demo-write-through-cache
.
├── README.md                   # README.md
├── app.py                      # flask app
├── docker-compose.yml          # docker-compose, what am I starting up?
├── dockerfile                  # docker config, how am I staring up?
├── init-db                     # db init scripts
│   └── create_users_table.sql  # create empty table in psql
├── requirements.txt            # python requirements
└── wait-for-it.sh              # Script to wait for services to be available
```

##### Clone this repo
```
git clone git@github.com:iblaine/demo-write-through-caches.git
```

##### Build this project
```
docker-compose down -v # as needed
docker-compose up --build
```

##### You should see this
```
docker ps
CONTAINER ID   IMAGE                          COMMAND                  CREATED          STATUS         PORTS                              NAMES
838c9068c171   demo-write-through-cache-web   "python app.py"          8 minutes ago    Up 3 minutes   5000/tcp, 0.0.0.0:5001->5001/tcp   demo-write-through-cache-web-1
0bbc9c774920   redis:latest                   "docker-entrypoint.s…"   14 minutes ago   Up 3 minutes   0.0.0.0:6379->6379/tcp             demo-write-through-cache-redis-1
ea9959cb6d51   postgres:latest                "docker-entrypoint.s…"   14 minutes ago   Up 3 minutes   0.0.0.0:5432->5432/tcp             demo-write-through-cache-postgres-1
```

##### Create a user
```
curl -X POST http://localhost:5001/user -H "Content-Type: application/json" -d '{"id": "1", "info": "Test User"}'
{"message":"User created/updated successfully.","status":"success"}
```

##### Verifiy your new user exists in psql
```
docker exec -it demo-write-through-cache-postgres-1 psql -U user -d exampledb
SELECT * FROM users WHERE id = '1';
```

##### Verifiy your new user exists in redis
```
docker exec -it demo-write-through-cache-redis-1 redis-cli
GET 1
```

###### get record, notice it comes from redis
```
curl http://localhost:5001/user/1
{"id":"1","info":"Test User","source":"redis"}
```

###### delete cache of this record in redis
```
docker exec -it demo-write-through-cache-redis-1 redis-cli
DEL 1
```

###### get record again, this time from psql
```
curl http://localhost:5001/user/1
{"id":"1","info":"Test User","source":"psql"}
```





