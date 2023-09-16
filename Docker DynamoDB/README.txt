
## Run
```bash

	java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
```


## Docker Compose
```bash
	docker-compose up
```


## Commands  as local host
```bash
	aws dynamodb list-tables --endpoint-url http://localhost:8000
```