  
FROM marvinbuss/aml-docker:1.10.0

LABEL maintainer="azure/gh_aml"

COPY /code /code
ENTRYPOINT ["/code/entrypoint.sh"]
