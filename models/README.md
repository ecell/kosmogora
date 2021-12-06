# Requirements

## A view file

- A Cytoscape JSON file (https://js.cytoscape.org/#notation/elements-json)
- The file name should end with `.cyjs`.
- The file name must correspond to the model name (`sample1.cyjs` -> `sample1`).
- Nodes must have
    - `positions` (`x` and `y`)
    - `name` and `shared_name` corresponding to a Species id in a model file.
- Edges must have
    - `source` and `target`
    - `name` and `shared_name` corresponding to a Reaction id in a model file.

## A model file

- A SBML file for COBRA (https://cobrapy.readthedocs.io/en/latest/io.html#SBML)
- The file name should end with `.xml`.
- The file name must correspond to the model name (`sample1.xml` -> `sample1`).
