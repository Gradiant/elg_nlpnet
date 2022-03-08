
# ``nlpnet`` Natural Language Processing with neural networks

nlpnet is a Python library for Natural Language Processing tasks based on neural networks. 
This repository contains a dockerized API built over nlpnet for integrate it into the ELG. This implementation performs part-of-speech tagging and semantic role labeling.

Its original code can be found here https://github.com/erickrf/nlpnet.

## Install
```
sh docker-build.sh
```
## Run
```
docker run --rm -p 0.0.0.0:5000:5000 --name nlpnet elg_nlpnet
```

## Use
- Tagger : two types:
  - Part of Speach (POS):
    ```
    curl -X POST  http://127.0.0.1:5000/tag_process -H 'Content-Type: application/json' -d '{ "type":"text", "content":"O rato roeu a roupa do rei de Roma.", "params":{"task":"pos"} }'
    ```
  - Semantic Role Labeling (SRL)
    ```
    curl -X POST  http://127.0.0.1:5000/tag_process -H 'Content-Type: application/json' -d '{ "type":"text", "content":"O rato roeu a roupa do rei de Roma.", "params":{"task":"srl"} }'
    ```

## Test
In the folder `test` you have the files for testing the API according to the ELG specifications.
It uses an API that acts as a proxy with your dockerized API that checks both the requests and the responses.
For this follow the instructions:

1) Launch the test:  `sudo docker-compose --env-file nlpnet.env up`

2) Make the requests, instead of to your API's endpoint, to the test's endpoint:
   ```
      curl -X POST  http://0.0.0.0:8866/processText/service -H 'Content-Type: application/json' -d '{ "type":"text", "content":"O rato roeu a roupa do rei de Roma.", "params":{"task":"pos"} }'
   ```
3) If your request and the API's response is compliance with the ELG API, you will receive the response.
   1) If the request is incorrect: Probably you will don't have a response and the test tool will not show any message in logs.
   2) If the response is incorrect: You will see in the logs that the request is proxied to your API, that it answers, but the test tool does not accept that response. You must analyze the logs.
   
## Citation
The original work of this tool is:
- https://github.com/erickrf/nlpnet
- SRL Model: Fonseca, E. R. and Rosa, J.L.G. A Two-Step Convolutional Neural Network Approach for Semantic Role Labeling. Proceedings of the 2013 International Joint Conference on Neural Networks, 2013. p. 2955-2961
- PoS Model: Fonseca, E. R. and Rosa, J.L.G. Mac-Morpho Revisited: Towards Robust Part-of-Speech Tagging. Proceedings of the 9th Brazilian Symposium in Information and Human Language Technology, 2013. p. 98-107
- More info: http://nilc.icmc.usp.br/nlpnet/
