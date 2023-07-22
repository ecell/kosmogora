#!/bin/sh

pip install -r requirements.txt
cd ./models
if [ ! -e bigg_models_reactions.txt ]; then
	wget http://bigg.ucsd.edu/static/namespace/bigg_models_reactions.txt
fi

if [ ! -e bigg_models_metabolites.txt ]; then
	wget http://bigg.ucsd.edu/static/namespace/bigg_models_metabolites.txt
fi

if [ ! -e id2id.tsv ]; then
	wget https://github.com/ecell/id2id/releases/download/test2/id2id.tsv
fi

if [ ! -e reac_prop.tsv ]; then
	wget https://www.metanetx.org/cgi-bin/mnxget/mnxref/reac_prop.tsv
fi

cd ..

python obj_manager.py -c

echo "Run following command."
echo "uvicorn --port 8000 app:app"
