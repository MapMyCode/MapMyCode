import networkx as nx
import os
import ast
import re

exclude_dirs = ['.venv','__pycache__','venv','mapmycode','.test-env','dist']

def walk_directories(path):
    python_files = []

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py") and file != "topological_sort.py":
                python_files.append(os.path.join(root, file))

    return python_files


def search_import(parent, child, parent_content):
    try:
        tree = ast.parse(parent_content,filename=parent)
    except SyntaxError:
        return False

    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            base_module = node.module if node.module else ""
            
            if base_module:
                imported_modules.add(base_module)
            
            for alias in node.names:
                if base_module:
                    imported_modules.add(f"{base_module}.{alias.name}")
                else:
                    imported_modules.add(alias.name)
    
    parent_tokens = parent.split('/')
    child_tokens = child.split('/')
    common = [tok for tok in parent_tokens if tok in child_tokens]
    import_name = ".".join([tok for tok in child_tokens if tok not in common])
    import_name = re.sub(".py","",import_name)
    if import_name in imported_modules:
        return True
    return False
    

def create_graph(python_files):
    graph = nx.DiGraph()
    file_contents = {}
    for i in range(len(python_files)):
        with open(python_files[i],'r') as f:
            current_content = f.read()
            
        file_contents[python_files[i]] = current_content        
        for j in range(len(python_files)):
            
            if i == j:
                continue
            
            if search_import(python_files[i],python_files[j],current_content):
                graph.add_edge(python_files[i],python_files[j])
    
    return graph, file_contents

def generate_weakly_connected_components_and_build_order(graph):
    weak_connected_components = nx.weakly_connected_components(graph)
    build_order = {}
    for index, component in enumerate(weak_connected_components):
        subgraph = graph.subgraph(component).copy()
        topological_sort_order = list(reversed(list(nx.topological_sort(subgraph))))
        build_order[f"C_{index+1}"] = topological_sort_order

    return build_order
    
        

if __name__ == "__main__":
    path = 'assignment1/'
    python_files = walk_directories(path)
    print(len(python_files))
    graph,file_contents = create_graph(python_files)
    print(graph)
    build_order = generate_weakly_connected_components_and_build_order(graph)
    print(build_order)