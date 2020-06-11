  
FROM marvinbuss/aml-docker:1.7.0

LABEL maintainer="azure/gh_aml"

COPY /code /code
ENTRYPOINT ["/code/entrypoint.sh"]
