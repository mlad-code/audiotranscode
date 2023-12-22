FROM intel/intel-optimized-ffmpeg

ENV CLOUDSDK_CORE_DISABLE_PROMPTS=1

RUN apt update \ 
    && apt install -y --no-install-recommends util-linux curl mediainfo \
    && curl -sSL https://sdk.cloud.google.com/ | bash

ENV PATH $PATH:/root/google-cloud-sdk/bin

COPY ./entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/bin/sh", "-c", "/entrypoint.sh"]
