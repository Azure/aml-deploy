FROM ghcr.io/marvinbuss/aml-docker:1.27.0

LABEL maintainer="azure/gh_aml"

COPY /code /code
ENTRYPOINT ["/code/entrypoint.sh"]
