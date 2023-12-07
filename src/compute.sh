#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 generate_routes_graph.py
python3 compute_adjacency_matrix.py
