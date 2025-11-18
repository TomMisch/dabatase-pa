# OSF → Project hub and preregistration (with links to GitHub & Zenodo)

**Purpose**: The Open Science Framework is your central public project page — the single point of entry for anyone who wants to understand, verify, or replicate your work.
## What to include:
- A short project title and abstract (like “Mapping the Public Administration Field Using OpenAlex”);
- A rationale for using OpenAlex (open, transparent, replicable);
- Preregistration of your research design (your methods, data sources, inclusion/exclusion criteria, and analysis plan);
- Documentation: upload PDFs or markdown summaries explaining each stage (data retrieval, cleaning, analysis);
- Links to:
    - your GitHub repository (for code and active development);
    - your Zenodo dataset (for archived versions);
    - your ORCID profile (for authorship verification).

## Why it matters:
OSF provides an official timestamp and a persistent link. It shows reviewers that your research plan existed before data analysis — evidence of transparency and rigour.

# GitHub → Scripts, README, and continuous development

**Purpose**: GitHub is your version-controlled workspace for coding, documentation, and workflow management.
## What to include:
- All Python scripts for data harvesting, cleaning, merging, matching, and analysis;
- README.md file explaining:
    - project overview and goals;
    - setup instructions;
    - dependencies and installation commands;
    - how to reproduce analyses.
- Folder structure for organisation;
- CITATION.cff file with project citation info;
- .zenodo.json (or enable Zenodo–GitHub link) for automatic DOI generation upon release;
- Issues and Wiki tabs for notes or ongoing improvements.
## Why it matters:
GitHub ensures every change is logged, reviewable, and revertible — crucial for open science credibility. It’s where development happens.

# Zenodo → Archived releases (with DOI, linked to GitHub)

**Purpose**: Zenodo is your long-term archive, providing a fixed, citable snapshot of your project.
## What to include:
- Periodic releases (e.g. v1.0 Initial data retrieval, v1.1 Cleaning and matching scripts, v2.0 Extended analysis);
- For each release:
    - a ZIP of your code and data (if open);
    - metadata description (authors, funding, keywords, abstract);
    - link to OSF and GitHub.
- Zenodo automatically assigns a DOI for each release and a concept DOI for the entire project.
## Why it matters:
Unlike GitHub, Zenodo guarantees permanence. Reviewers and future researchers can cite an exact version of your workflow.

# ORCID → Connects everything to your academic identity

**Purpose**: ORCID is your persistent researcher ID — it ensures that every dataset, preregistration, and publication is traceable to you.
## What to include:
- Add your OSF project, Zenodo deposit, and data paper DOIs to your ORCID record.
- Use your ORCID when registering on OSF, Zenodo, or submitting publications.
## Why it matters:
ORCID provides author identity continuity — key for tenure, grants, and credibility in open research ecosystems.

# (Later) Data paper / protocols.io → Peer-reviewed legitimacy

**Purpose**: Once your OpenAlex-based workflow stabilises, formalise it in a peer-reviewed outlet.
## Options:
- Data paper (e.g., Scientific Data, Data in Brief): describes your dataset and collection/cleaning process;
- Method paper (e.g., Journal of Open Research Software): explains the technical workflow;
- Protocols.io: step-by-step, citable guide (useful for the data retrieval and cleaning pipeline).
## Why it matters:
Formal publication not only validates your approach but also makes your methods part of the scholarly record — dispelling scepticism about OpenAlex-based data.

