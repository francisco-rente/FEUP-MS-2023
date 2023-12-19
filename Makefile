venv/bin/activate: requirements.txt
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

debug: venv/bin/activate src/debug.py
	venv/bin/python3 src/debug.py

results/graph.gpickle: venv/bin/activate src/generate_graph.py
	venv/bin/python3 src/generate_graph.py --gtfs datasets/gtfs-stcp datasets/gtfs-mdp --wf 0.05 0.01 --shapes true false --gpkg datasets/BGRI2021_1312.gpkg --out results/graph.gpickle

view-routes: venv/bin/activate results/graph.gpickle src/view_routes.py
	venv/bin/python3 src/view_routes.py results/graph.gpickle

view-metro: venv/bin/activate results/graph.gpickle src/view_routes.py
	venv/bin/python3 src/view_routes.py --routes A B Bexp C D E F -- results/graph.gpickle