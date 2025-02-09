venv/bin/activate: requirements.txt
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

# ================================== GRAPH ==================================

results/graph.gpickle: venv/bin/activate src/generate_graph.py
	venv/bin/python3 src/generate_graph.py --gtfs datasets/gtfs-stcp datasets/gtfs-mdp --wf 0.05 0.01 --shapes true false --gpkg datasets/BGRI2021_1312.gpkg --out results/graph.gpickle

# args: node
results/graph_without_$(node).gpickle: venv/bin/activate results/graph.gpickle src/delete_node.py
	venv/bin/python3 src/delete_node.py results/graph.gpickle $(node) results/graph_without_$(node).gpickle

view_routes: venv/bin/activate results/graph.gpickle src/view_routes.py
	venv/bin/python3 src/view_routes.py results/graph.gpickle

view_mdp: venv/bin/activate results/graph.gpickle src/view_routes.py
	venv/bin/python3 src/view_routes.py --routes A B Bexp C D E F -- results/graph.gpickle

# ================================== SHORTEST PATHS ==================================

# args: batches, batch_num
compute_shortest_paths: venv/bin/activate results/graph.gpickle src/compute_shortest_paths.py
	venv/bin/python3 -O src/compute_shortest_paths.py results/graph.gpickle --batch $(batches) $(batch_num) results/shortest_paths_group_$(batch_num).csv

debug_compute_shortest_paths: venv/bin/activate results/graph.gpickle src/compute_shortest_paths.py
	venv/bin/python3 src/compute_shortest_paths.py results/graph.gpickle results/debug.csv

# args: node
results/paths_affected_by_$(node).csv: venv/bin/activate results/shortest_paths_raw.csv src/filter_paths_affected.py
	venv/bin/python3 src/filter_paths_affected.py results/shortest_paths_raw.csv $(node) results/paths_affected_by_$(node).csv

# args: node, batches, batch_num
compute_partial_shortest_paths: venv/bin/activate results/graph_without_$(node).gpickle results/paths_affected_by_$(node).csv src/compute_partial_shortest_paths.py
	venv/bin/python3 -O src/compute_partial_shortest_paths.py results/graph_without_$(node).gpickle results/paths_affected_by_$(node).csv --batch $(batches) $(batch_num) results/shortest_paths_without_${node}_group_${batch_num}.csv

# ================================== VALIDATIONS ==================================

extract_validations: venv/bin/activate datasets/TIP_Validations/Porto\ Digital\ Ferrov\ 2023 datasets/TIP_Validations/Porto\ Digital\ Rodov\ 2023 src/extract_validations.py
	venv/bin/python3 src/extract_validations.py 'datasets/TIP_Validations/Porto Digital Ferrov 2023' Est/Op Validações results/mdp_validations.csv
	venv/bin/python3 src/extract_validations.py 'datasets/TIP_Validations/Porto Digital Rodov 2023' Paragem Validações results/stcp_validations.csv

results/network_validations.csv: venv/bin/activate results/mdp_validations.csv results/stcp_validations.csv datasets/gtfs-mdp datasets/gtfs-stcp src/match_validations_id.py
	venv/bin/python3 src/match_validations_id.py \
	--validations results/mdp_validations.csv results/stcp_validations.csv \
	--gtfs datasets/gtfs-mdp datasets/gtfs-stcp \
	-- results/network_validations.csv

results/validations_per_section.csv: venv/bin/activate results/network_validations.csv datasets/BGRI2021_1312.gpkg src/compute_validations_per_section.py
	venv/bin/python3 src/compute_validations_per_section.py results/network_validations.csv datasets/BGRI2021_1312.gpkg results/validations_per_section.csv	

results/network_validations_without_trindade.csv: results/network_validations.csv
	grep -v "Trindade" results/network_validations.csv > results/network_validations_without_trindade.csv

results/validations_per_section_without_trindade.csv: venv/bin/activate results/network_validations_without_trindade.csv datasets/BGRI2021_1312.gpkg src/compute_validations_per_section.py
	venv/bin/python3 src/compute_validations_per_section.py results/network_validations_without_trindade.csv datasets/BGRI2021_1312.gpkg results/validations_per_section_without_trindade.csv	

# ================================== STATISTICS SUPPORT ==================================

results/average_weight_to_section.csv: venv/bin/activate results/shortest_paths_raw.csv src/average_weight_to_section.py
	venv/bin/python3 src/average_weight_to_section.py results/shortest_paths_raw.csv results/average_weight_to_section.csv

results/average_weight_to_section_without_trindade.csv: venv/bin/activate results/shortest_paths_without_5726.csv src/average_weight_to_section.py
	venv/bin/python3 src/average_weight_to_section.py results/shortest_paths_without_5726.csv results/average_weight_to_section_without_trindade.csv

results/stops_count.csv: venv/bin/activate results/shortest_paths_raw.csv src/evaluate/compute_stops_count.py
	venv/bin/python3 src/evaluate/compute_stops_count.py results/shortest_paths_raw.csv results/stops_count.csv

results/stops_count_without_trindade.csv: venv/bin/activate results/shortest_paths_without_5726.csv src/evaluate/compute_stops_count.py
	venv/bin/python3 src/evaluate/compute_stops_count.py results/shortest_paths_without_5726.csv results/stops_count_without_trindade.csv

# ================================== STATISTICS ==================================

# Not really used
compute_distance_routes: venv/bin/activate results/graph.gpickle results/shortest_paths_raw.csv src/evaluate/compute_distance_routes.py
	venv/bin/python3 src/evaluate/compute_distance_routes.py results/graph.gpickle results/shortest_paths_raw.csv results/shortest_paths_distance_routes.csv

compute_average_weight: venv/bin/activate results/shortest_paths_raw.csv results/shortest_paths_without_5726.csv src/evaluate/compute_average_weight.py
	venv/bin/python3 src/evaluate/compute_average_weight.py results/shortest_paths_raw.csv
	venv/bin/python3 src/evaluate/compute_average_weight.py results/shortest_paths_without_5726.csv

compute_indicator: venv/bin/activate results/validations_per_section.csv results/average_weight_to_section.csv src/compute_indicator.py
	venv/bin/python3 src/compute_indicator.py results/validations_per_section.csv results/average_weight_to_section.csv results/indicator.csv

compute_indicator_without_trindade: venv/bin/activate results/validations_per_section_without_trindade.csv results/average_weight_to_section_without_trindade.csv src/compute_indicator.py
	venv/bin/python3 src/compute_indicator.py results/validations_per_section_without_trindade.csv results/average_weight_to_section_without_trindade.csv results/indicator_without_trindade.csv

analyse_stops_usage: venv/bin/activate results/network_validations.csv results/stops_count.csv src/evaluate/analyse_stops_usage.py
	venv/bin/python3 src/evaluate/analyse_stops_usage.py results/network_validations.csv results/stops_count.csv

# Not really useful as by removing Trindade we're not dispersing its validations across the adjacent stops!
analyse_stops_usage_without_trindade: venv/bin/activate results/network_validations_without_trindade.csv results/stops_count_without_trindade.csv src/evaluate/analyse_stops_usage.py
	venv/bin/python3 src/evaluate/analyse_stops_usage.py results/network_validations_without_trindade.csv results/stops_count_without_trindade.csv
