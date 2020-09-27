FROM ghcr.io/marvinbuss/aml-docker:1.14.0

LABEL maintainer="azure/gh_aml"

COPY /code /code
ENTRYPOINT ["/code/entrypoint.sh"]
