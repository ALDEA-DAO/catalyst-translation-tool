FROM python:3.8
RUN apt-get update
RUN apt-get install -y jq zip
RUN pip install awscli
RUN apt-get install -y dos2unix
COPY entrypoint.sh /entrypoint.sh
RUN dos2unix /entrypoint.sh && apt-get --purge remove -y dos2unix && rm -rf /var/lib/apt/lists/*
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
