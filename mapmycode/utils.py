import os
import base64
import io, requests
from PIL import Image as im
import matplotlib.pyplot as plt
from mapmycode.groq_call import run_groq_api
from mapmycode.prompts import get_mermaid_flowchart_prompt, get_documentation_prompt,get_incremental_documentation_prompt
import tiktoken
import time

DEFAULT_EXCLUDE_DIRS = ['.venv','__pycache__','venv','mapmycode','.test-env','dist']

def walk_directories(path, extra_exclude_dirs=None):
    python_files = []
    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS) | set(extra_exclude_dirs or [])

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py") and file != "topological_sort.py":
                python_files.append(os.path.join(root, file))

    return python_files

def create_documentation(files_metadata,path):
    
    encoding = tiktoken.get_encoding("o200k_base")
    max_limit = 6000
    
    file_names = files_metadata.keys()
    start = 0
    existing_documentation = ""
    while start < len(file_names):
        context = files_metadata[file_names[start]]
        tokens = len(encoding.encode(context))
        if tokens > max_limit:
            prompt = get_incremental_documentation_prompt(context,existing_documentation)
            existing_documentation = run_groq_api(prompt)
            start += 1
            time.sleep(2)
        else:
            for k in range(start, len(file_names)):
                new_context = files_metadata[file_names[k]]
                new_tokens = len(encoding.encode(new_context))
                
                total_tokens = len(encoding.encode(context)) + new_tokens
                
                if total_tokens > max_limit:
                    start = k
                    break
                
                context += new_context
            
            prompt = get_incremental_documentation_prompt(context,existing_documentation)
            existing_documentation = run_groq_api(prompt)
            time.sleep(2)
            
    path = os.path.join(path,"documentation.md")
    with open(path,'w') as f:
        f.write(existing_documentation)
    
    return existing_documentation
    

def mm(graph, base_dir):
    graphbytes = graph.encode("utf8")
    base64_bytes = base64.urlsafe_b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")
    img = im.open(io.BytesIO(requests.get('https://mermaid.ink/img/' + base64_string).content))
    plt.imshow(img)
    plt.axis('off') # allow to hide axis
    image_path = os.path.join(base_dir, "image.png")
    plt.savefig(image_path, dpi=1200)
    
    
def create_mermaid_diagram(graph,documentation,path):
    mermaid_prompt = get_mermaid_flowchart_prompt(documentation,graph)
    response = run_groq_api(mermaid_prompt)
    response = response.replace("```mermaid", "").replace("```", "").strip()
    mermaid_syntax_path = os.path.join(path,'mermaid_syntax.txt')
    with open(mermaid_syntax_path,'w') as f:
        f.write(response)
    mm(response,path)
    
