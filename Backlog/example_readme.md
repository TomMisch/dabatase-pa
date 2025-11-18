# OpenAlex Data Retrieval – Public Administration Snapshot
**Retrieval date:** 1 March 2025  
**Responsible:** Fulvio Scognamiglio  
**Script version:** v1.0 (retrieval.py)  
**OSF registration:** https://osf.io/XXXX  
**GitHub repository:** https://github.com/FulvioScognamiglio/openalex-pa-retrieval  
**Zenodo archive:** https://doi.org/10.5281/zenodo.XXXXXX  

## Description
This dataset contains all records retrieved from OpenAlex corresponding to the *Public Administration* field, operationalised through the JCR SSCI and ESCI Public Administration category journals.

## Query parameters
- Endpoint: `https://api.openalex.org/works`
- Filter: `concept.id:C154945302, type:journal-article, publication_year:2000-2024`
- Per-page: 200  
- Pagination: cursor-based  
- API version: v1 (release 2025-02-15)  
- User agent: `"OpenAlex PA Snapshot – FulvioScognamiglio (London South Bank University)"`

## Data content
Each record contains the following metadata fields:
`id, doi, title, abstract_inverted_index, authorships, host_venue, publication_year, cited_by_count, referenced_works, concepts, open_access, grants, language, is_paratext, type, oa_url`

## File formats
- `openalex_retrieval_2025-03-01.jsonl` – Raw output from the API (JSON Lines format)
- `openalex_retrieval_2025-03-01.csv` – Flattened version for descriptive checks
- `retrieval_log_2025-03-01.txt` – Log of API calls and progress
- `error_log_2025-03-01.txt` – Any failed requests or anomalies

## Notes and anomalies
- No records found for years before 2000.  
- ~0.7% of records returned null `doi`.  
- Some pagination resets due to API rate limits; corrected via automatic retries.  
- Abstract reconstruction successful for 98% of records; missing for the remainder due to empty inverted indexes.

## Licence and access
These metadata are distributed under the [CC0 1.0 Universal Licence](https://creativecommons.org/publicdomain/zero/1.0/), consistent with OpenAlex policy.  
Derived datasets (cleaned and merged versions) will be shared under separate terms.
