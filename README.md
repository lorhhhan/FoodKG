
FOOD KNOWLEDGE GRAPH

This project implements a food and nutrition knowledge graph as part of the Intelligent Medical Service Platform. It integrates dish, ingredient, and nutrition information using a Neo4j graph database, enabling semantic-level queries and personalized health recommendations. 

Directory Structure
data/
    Contains CSV files including node tables, edge tables, and food ingredient dictionaries used for building the knowledge graph.

build_graph.py
    A Python script to build the knowledge graph. It reads structured CSV tables and populates the Neo4j graph database with dish, ingredient, and nutrition nodes and their relationships.

views.py
    Backend logic for the Django server. Implements RESTful APIs for question answering (/api/qa/), fuzzy matching (/api/suggestions/), user login, and graph data querying.

templates/
    HTML templates used with Django for frontend interface. Supports visualization and user interaction with the graph.

Instructions to Run:
1. Run `build_graph.py` to construct the knowledge graph.
2. Launch the Django server using:
       python manage.py runserver
3. Open the web interface at:
       http://127.0.0.1:8000/main

The platform allows users to ask questions about dishes, ingredients, and nutrients, view associated data through interactive graph visualization, and receive health guidance based on structured knowledge.



