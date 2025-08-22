 
### Build application
Build the Docker image manually by cloning the Git repo.
```
 
$ docker build -t contec/deepblu-report .
```

### Download precreated image
 
```
docker rm deepblu-report && docker run -e TZ=America/Los_Angeles --name deepblu-report -v C:/Users/mprabu/Projects/deepblu-report:/app -p 8989:8989 contec/deepblu-report
```
 