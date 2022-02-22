FROM ubuntu:18.04



RUN apt-get update -y \
    && apt-get install -y python3-pip python3-dev \
    && apt-get install -y wget \
	&& apt-get install -y unzip \
	&& rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip
RUN pip3 install flask flask_json
RUN pip3 install numpy

ENV LANG="C.UTF-8" \
    LC_ALL="C.UTF-8"

RUN mkdir -p nlpnet

WORKDIR /nlpnet/
RUN wget https://github.com/erickrf/nlpnet/archive/refs/heads/master.zip
RUN unzip master
WORKDIR ./nlpnet-master
RUN chmod -R 777 ./*
RUN pip3 install .

WORKDIR /nlpnet/
RUN mkdir -p ./models/
WORKDIR ./models/

#Download models
RUN wget http://nilc.icmc.usp.br/nlpnet/data/pos-pt.tgz
RUN tar xvzf pos-pt.tgz
RUN wget http://nilc.icmc.usp.br/nlpnet/data/srl-pt.tgz
RUN tar xvzf srl-pt.tgz


EXPOSE 5000

#Download nltk
WORKDIR /nlpnet/
COPY ./ /nlpnet/
RUN python3 -m nltk.downloader punkt

CMD ["python3", "server.py"]