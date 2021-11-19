# ==================================================================================
#  This SW is developed as part of ITU-5G-AI/ML challenge
#  ITU-ML5G-PS-014: Build-a-thon(PoC) Network resource allocation
#  for emergency management based on closed loop analysis
#  Team : RAN-RIC-xApp
#  Author : Deena Mukundan
#  Description : This file has the main implementation of predictor xApp
# ==================================================================================
FROM frolvlad/alpine-miniconda3
# RMR setup
RUN mkdir -p /opt/route/

# copy rmr files from builder image in lieu of an Alpine package
COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.0.5 /usr/local/lib64/librmr* /usr/local/lib64/

COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.0.5 /usr/local/bin/rmr* /usr/local/bin/
ENV LD_LIBRARY_PATH /usr/local/lib/:/usr/local/lib64
COPY local.rt /opt/route/local.rt
ENV RMR_SEED_RT /opt/route/local.rt


RUN apk update && apk add gcc musl-dev
RUN pip install ricxappframe

# Install
COPY setup.py /tmp

# RUN mkdir -p /tmp/ad/
COPY src/ /alloc
COPY conf/ /alloc
COPY xapp-descriptor/ /alloc
ENV CONFIG_FILE=/alloc/config.json
RUN pip install /tmp
ENV PYTHONUNBUFFERED 1
CMD PYTHONPATH=/ad:/usr/lib/python3.7/site-packages/:$PYTHONPATH run-alloc.py
