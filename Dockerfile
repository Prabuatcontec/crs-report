FROM  python:3.9-slim-buster

ENV DEBIAN_FRONTEND noninteractive

MAINTAINER  Prabu "<prabum1985@gmail.com>"
ENV TZ=America/Danmarkshavn

COPY requirements.txt .
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update --fix-missing\
    && apt-get install build-essential -y \
        && apt-get install -yq

RUN apt-get update \    
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update -y && apt-get update \
  && apt-get install -y --no-install-recommends curl gcc g++ gnupg unixodbc cron nano libgssapi-krb5-2 curl apt-transport-https

RUN apt-get update  \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev
    
RUN pip install --upgrade pip \
    && pip install mysqlclient \
    && pip install -r requirements.txt 
COPY openssl.cnf /etc/ssl/openssl.cnf
COPY . /app
WORKDIR /app

EXPOSE 8989
ENTRYPOINT ["python"]
CMD ["src/app.py"]
