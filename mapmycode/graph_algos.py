from mapmycode.groq_call import run_groq_api
from mapmycode.prompts import get_file_summary, get_chunk_summary_prompt
from langchain_core.output_parsers import JsonOutputParser
import os
from mapmycode.pydantic_classes import FileSummary
import json
import time
import tiktoken

MAX_FILE_CONTENT_TOKENS = 6000
CHUNK_TOKENS = 4000

def topological_sort(graph):
    visited = set()
    stack = []

    def dfs(node):
        if node in visited:
            return
        
        visited.add(node)

        for neighbor in graph[node]:
            dfs(neighbor)

        stack.append(node)

    for node in graph:
        dfs(node)

    return stack


def create_graph(python_files):
    graph = {}
    file_contents = {}
    for i in range(len(python_files)):
        with open(python_files[i],'r') as f:
            current_content = f.read()
            
        file_contents[python_files[i]] = current_content
        graph[python_files[i]] = []
        
        for j in range(len(python_files)):
            
            if i == j:
                continue
            
            search_term = "from " + python_files[j][:-3]
            #module_name = python_files[j].replace("/", ".").replace("\\", ".")[:-3]
            #search_term = f"from {module_name}"
            if search_term in current_content:
                graph[python_files[i]] += [python_files[j]]
    
    return graph, file_contents

def summarize_large_file_content(file_name, file_content):
    encoding = tiktoken.get_encoding("o200k_base")

    if len(encoding.encode(file_content)) <= MAX_FILE_CONTENT_TOKENS:
        return file_content

    running_summary = ""
    chunk_lines = []
    chunk_tokens = 0

    for line in file_content.splitlines(keepends=True):
        line_tokens = len(encoding.encode(line))

        if chunk_lines and chunk_tokens + line_tokens > CHUNK_TOKENS:
            chunk_prompt = get_chunk_summary_prompt(file_name, "".join(chunk_lines), running_summary)
            running_summary = run_groq_api(chunk_prompt)
            time.sleep(2)
            chunk_lines = []
            chunk_tokens = 0

        chunk_lines.append(line)
        chunk_tokens += line_tokens

    if chunk_lines:
        chunk_prompt = get_chunk_summary_prompt(file_name, "".join(chunk_lines), running_summary)
        running_summary = run_groq_api(chunk_prompt)

    return running_summary

def create_dependency_dict(graph,order,file_contents):
    results = {}
    parser = JsonOutputParser(pydantic_object=FileSummary)
    for file in order:
        file_content = summarize_large_file_content(file, file_contents[file])

        dependencies = graph[file]
        dependencies_dict = {}
        
        for dependency in dependencies:
            dependencies_dict[dependency] = results[dependency]['important_symbols']
        
        summary_prompt = get_file_summary(file,file_content, dependencies_dict)
        result = run_groq_api(summary_prompt)
        result_parsed = parser.parse(result)
        results[file] = result_parsed
        time.sleep(2)
    
    return results