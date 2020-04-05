  
FROM marvinbuss/aml-docker:1.1.5

LABEL maintainer="azure/gh_aml"

COPY /code /code
ENTRYPOINT ["/code/entrypoint.sh"]
