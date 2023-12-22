FROM intel/intel-optimized-ffmpeg

ENV CLOUDSDK_CORE_DISABLE_PROMPTS=1
ENV PYTHONUNBUFFERED True

RUN apt update \ 
    && apt install -y --no-install-recommends util-linux curl mediainfo \
    && curl -sSL https://sdk.cloud.google.com/ | bash

COPY requirements.txt ./
COPY ./entrypoint.sh /entrypoint.sh
RUN pip install -r requirements.txt

ENV PATH $PATH:/root/google-cloud-sdk/bin
#ENTRYPOINT ["/bin/sh", "-c", "/entrypoint.sh"]
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
