FROM python:3.12-slim AS base
# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-dotnet-configure-containers
RUN useradd -d /app -M -s /sbin/nologin -u 5678 -U appuser
USER appuser:appuser

FROM base AS slim
# Environment variable needed for read-only filesystem
ENV COMPlus_EnableDiagnostics=0

WORKDIR /app

#RUN apt update && apt install libgl1 -y

COPY requirements.txt .
RUN pip3 install -r requirements.txt && pip3 install typing-extensions --upgrade

RUN mkdir appconfig/ & \
mkdir applib/ & \
mkdir model/ & \
mkdir files/ & \
mkdir temp/ & \
mkdir UI/ & \
mkdir packages/ & 

COPY --chown=appuser:appuser packages/ packages/ 
RUN pip3 install packages/hcc2sdk-0.1.0-py3-none-any.whl

COPY --chown=appuser:appuser *.py ./ 
COPY --chown=appuser:appuser appconfig/ appconfig/ 
COPY --chown=appuser:appuser applib/ applib/
COPY --chown=appuser:appuser UI/ UI/
COPY --chown=appuser:appuser files/ files/

COPY --chown=appuser:appuser entry_point.sh .
RUN chmod +x entry_point.sh
USER root:root
RUN install -o appuser -g appuser -d -m 0755 /app/temp
RUN install -o appuser -g appuser -d -m 0755 /app/model
RUN install -o appuser -g appuser -d -m 0755 /app/files
RUN install -o appuser -g appuser -d -m 0755 /app/appconfig
USER appuser:appuser
ENTRYPOINT ["./entry_point.sh"]
#ENTRYPOINT [ "tail", "-f", "/dev/null" ]

LABEL org.opencontainers.image.authors="NGRTU Team <ngrtuteam@sensiaglobal.com>" \
      org.opencontainers.image.vendor="Sensia Global" \
      org.opencontainers.image.url="https://www.sensiaglobal.com/" \
      org.opencontainers.image.license="Propietary" \
      com.sensiaglobal.image.artifacts.source="sensia-edge-docker-dev"



