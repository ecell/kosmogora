#!/bin/sh

pip install -r requirements.txt
cd ./models
if [ ! -e bigg_models_reactions.txt ]; then
	wget http://bigg.ucsd.edu/static/namespace/bigg_models_reactions.txt
fi

if [ ! -e bigg_models_metabolites.txt ]; then
	wget http://bigg.ucsd.edu/static/namespace/bigg_models_metabolites.txt
fi

cd ..

python obj_manager.py -c

echo "Run following command."
echo "uvicorn --port 8000 app:app"
