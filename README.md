# answer\_talker

## Create Environments
We strongly recomend to make a separated python environment.

```
$ python -m venv env
$ source env/bin/activate
```

## Install dependencies

### Automaticaly

This process can be done by `preparation.sh` script (for LINUX and MacOS only).

### By hand

First, install dependent libraries.

```
$ pip install -r requirements.txt
```

Download database files and place them in `./models`.

```
wget http://bigg.ucsd.edu/static/namespace/bigg_models_reactions.txt
wget http://bigg.ucsd.edu/static/namespace/bigg_models_metabolites.txt
wget https://www.metanetx.org/cgi-bin/mnxget/mnxref/reac_prop.tsv
wget https://github.com/ecell/id2id/releases/download/test2/id2id.tsv
```

Run Initialization before launch server

```
$ python obj_manager.py -c
```

## Run the server

```
$ uvicorn --host [your ip address] --port 8000 app:app
```

Open your browser at `http://[your ip address]:8000/docs`.

![docs](./image/docs_image.png)

See more about FastAPI here: https://fastapi.tiangolo.com/

