# answer\_talker

## Create Environments
We strongly recomend to make a separated python environment.

```
$ python -m venv env
$ source env/bin/activate
```

## Install dependencies

### Automaticaly

This process can be done by `preparation.sh` script.



### By hand

install libraries.

```
$ pip install -r requirements.txt
```

download database files and place them in `./models`.

```
wget http://bigg.ucsd.edu/static/namespace/bigg_models_reactions.txt
wget http://bigg.ucsd.edu/static/namespace/bigg_models_metabolites.txt
```

Initialization before launch server

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

