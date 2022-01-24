# answer\_talker

Install `miniconda` first (https://docs.conda.io/en/latest/miniconda.html).

```
$ conda create -n answer_talker
$ conda activate answer_talker
```

Install libraries:

```
$ conda install -c conda-forge fastapi uvicorn cobra
```

Run the server with:

```
$ uvicorn --host [your ip address] --port 8000 app:app
```

Open your browser at `http://[your ip address]:8000/docs`.

See more about FastAPI here: https://fastapi.tiangolo.com/
