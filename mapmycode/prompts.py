def get_file_summary(file_name, file_content, dependencies_dict):
    summary_prompt = f"""
    You are analyzing a Python codebase for two downstream tasks:
    1. generating project documentation
    2. generating an architecture diagram

    You will be given:
    - file name: {file_name}
    - file content: {file_content}
    - dependencies: {dependencies_dict}

    Your goal is to extract ONLY the minimum high-value information needed for documentation and architecture understanding.

    Instructions:
    1. Identify the PRIMARY responsibility of this file in 1-2 sentences.
    2. Identify only the MOST IMPORTANT symbols defined in this file:
      - top-level functions that are central to the file's purpose
      - classes
      - entry-point functions
      - orchestration functions
      - public API functions
    3. DO NOT include trivial/private/helper functions unless they are essential to understanding the architecture.
    4. For each important symbol, return only:
      - name
      - type ("function" or "class")
      - short role in the file
    5. Summarize only MEANINGFUL dependencies that help explain architecture.
      - Ignore standard library imports unless they are central to the file’s responsibility.
      - Ignore dependencies that are imported but not materially important.
    6. Add a short "flow_role" describing how this file participates in the overall project flow.
      Examples:
      - "entry point"
      - "data loading"
      - "preprocessing"
      - "model training"
      - "inference"
      - "utility support"
      - "visualization"
      - "API layer"
      - "database access"
    7. Keep the output highly compressed.
    8. Output VALID JSON ONLY.

    Return JSON in exactly this schema:

    {{
      "file_name": "{file_name}",
      "file_purpose": "<1-2 sentence summary>",
      "flow_role": "<short architectural role>",
      "dependencies": [
        {{
          "dependency_name": "<string>",
          "role": "<short description of why this dependency matters>"
        }}
      ],
      "important_symbols": [
        {{
          "name": "<string>",
          "type": "function|class",
          "role": "<short description>"
        }}
      ]
    }}
    """
    return summary_prompt
  
def get_documentation_prompt(files_metadata):
    prompt = f"""
    You are an expert software architect, code analyst, and technical documentation writer.

    Your task is to produce clean and structured Markdown documentation for a Python codebase using the provided file metadata.

    The metadata may contain:
    - file names
    - summaries/objectives
    - functions and classes
    - dependency/import relationships
    - structural or architectural hints

    You must analyze the metadata and generate documentation that explains both the architecture and the purpose of the codebase.

    ---

    # Required Output Structure

    ## 1. Overall Codebase Objective
    Provide a high-level explanation of:
    - the purpose of the project
    - the problem it aims to solve
    - the kind of workflow or application it represents
    - the major capabilities suggested by the file structure

    ## 2. Logical Flow
    Describe the likely end-to-end flow of the codebase:
    - probable starting point or entry file(s)
    - how data or control moves across modules
    - how different files interact
    - the execution pipeline from beginning to end

    Where exact flow is not explicit, provide a reasoned inference.

    ## 3. File-wise Explanations
    For every file, create a subsection:

    ### <filename>
    Purpose:
    Key functions and classes:
    Role in the codebase:
    Notes:

    Write in plain sentences without special formatting.

    ## 4. File-wise Dependencies
    For every file:

    ### <filename>
    Depends on:
    Dependency purpose:
    Remarks:

    If no internal dependencies exist, state that clearly.

    ---

    # Writing Guidelines

    - Output clean Markdown without bold, italics, or special styling symbols.
    - Do not use **, *, or other decorative characters.
    - Keep formatting simple and readable.
    - Use headings, spacing, and plain text for structure.
    - Do not restate metadata directly; interpret it.
    - Do not invent unsupported details.
    - If something is uncertain, explicitly mention it as an inference.
    - Write for engineers who are new to the codebase.

    ---

    # Input
    Files metadata:
    {files_metadata}
    """
    return prompt
  

def get_incremental_documentation_prompt(existing_documentation,
new_files_metadata):    
  prompt = f"""
You are an expert software architect, code analyst, and technical documentation writer.

Your task is to maintain a concise living documentation file for a Python codebase.

The codebase metadata is provided in batches because the entire repository cannot be analyzed in a single request.

You will receive:

1. Existing documentation generated so far
2. A new batch of file metadata

Your job is to update the documentation using the newly discovered information.

--------------------------------------------------
CRITICAL LENGTH REQUIREMENT
--------------------------------------------------

The entire documentation MUST remain between 300 and 500 words.

This limit applies every time you generate output.

Do not allow the document to grow indefinitely.

When new information is introduced:

- Compress older descriptions if necessary.
- Merge related information into shorter summaries.
- Retain only the most important architectural insights.
- Prioritize major files and core modules.
- Summarize utility/helper files briefly.
- Remove redundant explanations.
- Rewrite sections to stay within the word budget.

Think of this as maintaining an executive technical summary rather than detailed documentation.

--------------------------------------------------
IMPORTANT RULES
--------------------------------------------------

- Treat the existing documentation as the current source of truth.
- Incorporate new findings into the documentation.
- Avoid duplicate information.
- Preserve the overall structure.
- Update previous conclusions if new evidence provides a better understanding.
- If information conflicts, prefer the newer metadata.
- Do not invent unsupported details.
- Explicitly mark uncertain conclusions as inferences.
- Focus on architecture, responsibilities, and interactions rather than implementation details.

--------------------------------------------------
OUTPUT REQUIREMENTS
--------------------------------------------------

Return the COMPLETE updated documentation.

Do NOT return only the delta.

Generate a fully rewritten and updated version that incorporates all known information while remaining between 300 and 500 words.

--------------------------------------------------
DOCUMENT STRUCTURE
--------------------------------------------------

# Overall Codebase Objective

A concise summary of:
- project purpose
- problem being solved
- key capabilities

# Logical Flow

A concise description of:
- entry points
- execution flow
- major module interactions

# Key Files

For each important file:

## <filename>

Purpose:
Role:
Notes:

Use only 1-3 short sentences per file.

If there are many files, group minor files together under a shared section such as:

## Supporting Utilities

Summarize their collective purpose briefly.

# Dependencies

Summarize only the most important dependency relationships and architectural connections.

--------------------------------------------------
EXISTING DOCUMENTATION
--------------------------------------------------

{existing_documentation}

--------------------------------------------------
NEW FILE METADATA
--------------------------------------------------

{new_files_metadata}

--------------------------------------------------
TASK
--------------------------------------------------

Produce the complete updated documentation while strictly maintaining a total length between 300 and 500 words.
"""
  return prompt

def get_mermaid_flowchart_prompt(
  documentation,
  dependency_graph):
  prompt = f"""
You are a Software Architecture Visualization Expert.

### TASK

Convert the provided codebase documentation and dependency graph into a Mermaid.js Flowchart that visualizes:

1. The role of each file/module
2. The overall architecture
3. How files interact
4. Dependency relationships between files
5. The end-to-end flow of the system

The documentation is the primary source of truth for understanding responsibilities and architecture.

The dependency graph is the source of truth for dependency relationships.

--------------------------------------------------
INPUTS
--------------------------------------------------

### CODEBASE DOCUMENTATION

{documentation}

### DEPENDENCY GRAPH

{dependency_graph}

--------------------------------------------------
HOW TO USE THE INPUTS
--------------------------------------------------

Use the documentation to determine:

- file purpose
- module responsibilities
- architectural role
- logical flow
- major functionality
- how files use their dependencies

Use the dependency graph to determine:

- file-to-file connections
- dependency directions
- relationship structure

Do not simply repeat dependency names.

Instead explain relationships in terms of architecture and responsibility.

Example:

Bad:
"Uses parser.py"

Good:
"Uses parsing utilities to extract and normalize source code information"

--------------------------------------------------
DIAGRAM GOAL
--------------------------------------------------

The resulting flowchart should help a new engineer quickly understand:

- What each file does
- How files collaborate
- Which files orchestrate workflows
- Which files provide reusable services/utilities
- The overall structure of the codebase

--------------------------------------------------
NODE FORMAT
--------------------------------------------------

Represent every file as a node.

Preferred format:

NodeID["<b>filename.py</b><br/>
Role: ...<br/>
Purpose: ...<br/>
Uses deps for: ..."]

Keep descriptions concise.

Maximum:
- 1 short role statement
- 1 short purpose statement
- 1 short dependency usage statement

Avoid long paragraphs.

--------------------------------------------------
EDGE RULES
--------------------------------------------------

Show all dependency relationships using arrows.

Example:

A --> B

Arrow direction means:

A depends on B

Add edge labels only when they improve clarity.

Example:

A -->|orchestrates| B

A -->|loads config| C

A -->|uses utilities| D

--------------------------------------------------
SUBGRAPH RULES
--------------------------------------------------

If modules appear to belong to common packages or directories:

Group them using Mermaid subgraphs.

Examples:

subgraph ingestion
subgraph processing
subgraph visualization
subgraph utilities

Only create groups when they improve readability.

--------------------------------------------------
ARCHITECTURE EMPHASIS
--------------------------------------------------

Use documentation to identify:

- Entry points
- Controllers/orchestrators
- Services
- Utilities
- Configuration modules
- Data models
- Shared components

Reflect these distinctions through layout and styling.

--------------------------------------------------
COLOR SCHEME
--------------------------------------------------

Entry Points / Orchestrators:
fill:#FFF4E5,stroke:#FB8C00,stroke-width:2px,color:#1F1F1F

Core Processing / Services:
fill:#E8F0FE,stroke:#1A73E8,stroke-width:1.5px,color:#1F1F1F

Utilities / Helpers:
fill:#E8F5E9,stroke:#43A047,stroke-width:1.5px,color:#1F1F1F

Config / Constants / Schemas:
fill:#F3E8FD,stroke:#8E24AA,stroke-width:1.5px,color:#1F1F1F

Apply styles consistently.

--------------------------------------------------
READABILITY RULES
--------------------------------------------------

- Keep node text compact.
- Prefer architectural summaries over implementation details.
- Avoid large blocks of text.
- Optimize for diagram readability.
- If documentation mentions many functions, include only the most important ones.
- Focus on responsibilities rather than exhaustive details.

--------------------------------------------------
OUTPUT REQUIREMENTS
--------------------------------------------------

Return ONLY a valid Mermaid code block.

Start exactly with:

```mermaid
flowchart TD
"""
  return prompt
