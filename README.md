 
### Build application
Build the Docker image manually by cloning the Git repo.
```
 
$ docker build -t contec/crs-report .
```

### Download precreated image
 
```
docker rm crs-report && docker run -e TZ=America/Los_Angeles --name crs-report -v C:/Users/mprabu/Projects/crs-report:/app -p 8990:8990 contec/crs-report
```
 