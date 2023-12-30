venv/bin/activate: requirements.txt
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

debug: venv/bin/activate src/debug.py
	venv/bin/python3 src/debug.py

results/graph.gpickle: venv/bin/activate src/generate_graph.py
	venv/bin/python3 src/generate_graph.py --gtfs datasets/gtfs-stcp datasets/gtfs-mdp --wf 0.05 0.01 --shapes true false --gpkg datasets/BGRI2021_1312.gpkg --out results/graph.gpickle

view_routes: venv/bin/activate results/graph.gpickle src/view_routes.py
	venv/bin/python3 src/view_routes.py results/graph.gpickle

view_mdp: venv/bin/activate results/graph.gpickle src/view_routes.py
	venv/bin/python3 src/view_routes.py --routes A B Bexp C D E F -- results/graph.gpickle

# args: batches, batch_num
compute_shortest_paths: venv/bin/activate results/graph.gpickle src/compute_shortest_paths.py
	venv/bin/python3 -O src/compute_shortest_paths.py results/graph.gpickle --batch $(batches) $(batch_num) results/shortest_paths_group_$(batch_num).csv

debug_compute_shortest_paths: venv/bin/activate results/graph.gpickle src/compute_shortest_paths.py
	venv/bin/python3 src/compute_shortest_paths.py results/graph.gpickle results/debug.csv

# args: node
results/graph_without_$(node).gpickle: venv/bin/activate results/graph.gpickle src/delete_node.py
	venv/bin/python3 src/delete_node.py results/graph.gpickle $(node) results/graph_without_$(node).gpickle

# args: node
results/paths_affected_by_$(node).csv: venv/bin/activate results/shortest_paths_raw.csv src/filter_paths_affected.py
	venv/bin/python3 src/filter_paths_affected.py results/shortest_paths_raw.csv $(node) results/paths_affected_by_$(node).csv

# args: node, batches, batch_num
compute_partial_shortest_paths: venv/bin/activate results/graph_without_$(node).gpickle results/paths_affected_by_$(node).csv src/compute_partial_shortest_paths.py
	venv/bin/python3 -O src/compute_partial_shortest_paths.py results/graph_without_$(node).gpickle results/paths_affected_by_$(node).csv --batch $(batches) $(batch_num) results/shortest_paths_without_${node}_group_${batch_num}.csv

compute_statistics: venv/bin/activate results/graph.gpickle results/shortest_paths_raw.csv src/evaluate/compute_distance_routes.py
	venv/bin/python3 src/evaluate/compute_distance_routes.py results/graph.gpickle results/shortest_paths_raw.csv results/shortest_paths_statistics.csv

compute_stops_count: venv/bin/activate results/shortest_paths_raw.csv src/evaluate/compute_stops_count.py
	venv/bin/python3 src/evaluate/compute_stops_count.py results/shortest_paths_raw.csv results/stops_count.csv

results/average_weight_to_node.csv: venv/bin/activate results/shortest_paths_raw.csv src/average_weight_to_node.py
	venv/bin/python3 src/average_weight_to_node.py results/shortest_paths_raw.csv results/average_weight_to_node.csv

extract_validations: venv/bin/activate datasets/TIP_Validations/Porto\ Digital\ Ferrov\ 2023 datasets/TIP_Validations/Porto\ Digital\ Rodov\ 2023 src/extract_validations.py
	venv/bin/python3 src/extract_validations.py 'datasets/TIP_Validations/Porto Digital Ferrov 2023' Est/Op Validações results/mdp_validations.csv
	venv/bin/python3 src/extract_validations.py 'datasets/TIP_Validations/Porto Digital Rodov 2023' Paragem Validações results/stcp_validations.csv
