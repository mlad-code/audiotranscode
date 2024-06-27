FROM google/cloud-sdk

ENV CLOUDSDK_CORE_DISABLE_PROMPTS=1
ENV PYTHONUNBUFFERED True

RUN apt update \ 
    && apt install -y --no-install-recommends util-linux mediainfo python3-pip ffmpeg

COPY requirements.txt ./
COPY ./entrypoint.sh /entrypoint.sh
RUN pip3 install -r requirements.txt

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY main.py ./

ENV PATH $PATH:/root/google-cloud-sdk/bin
#ENTRYPOINT ["/bin/sh", "-c", "/entrypoint.sh"]
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
