# Project Title

Public Administration Snapshot: Mapping the Field Using OpenAlex

# Project Description

This project aims to build a comprehensive, reproducible, and openly accessible bibliometric database of the Public Administration field using OpenAlex as the primary data source.

**The project will**:
- **Retrieve metadata** for relevant Public Administration records from **OpenAlex**;
- **Clean, harmonise, and enrich** the data for large-scale bibliometric analyses;
- **Produce reproducible analytical outputs** (e.g., publication trends, co-authorship networks, thematic clusters);
- **Publish all code and documentation under CC-BY Attribution-NonCommercial-ShareAlike 4.0 International**.
This preregistration outlines the initial research design, the data retrieval and cleaning plan, and the analytical intentions. By ensuring transparency in both the data collection and analytical processes, this work enables replication and verification of the correctness and fairness of the impact and performance evaluation, consistent with the principles of the Leiden Manifesto (Hicks et al. 2015)
**Future revisions** and updates will be registered as new components or registrations, depending on their impact to mantain full transparency of any changes.

## Research Objectives

The main goal of this project is to *create a reliable and updatable bibliometric snapshot of the Public Administration field**. The resulting database will contribute to the **science of science** research agenda within Public Administration, helping to uncover hidden patterns in scholarly production, collaboration, and impact.
Given the exploratory and infrastructural nature of this initiative, no specific hypotheses are defined at this stage. Instead, the focus is on developing a transparent and reproducible data and analysis pipeline that can later support multiple lines of research.

## Project Structure

The project will consist of the following stages:
1. Data Retrieval – harvesting metadata from OpenAlex;
2. Data Cleaning and Integration – deduplication, disambiguation, and harmonisation of metadata;
3. Data Enrichment – adding contextual metadata (e.g. country codes, journal metrics);
4. SQL Database Creation – structuring the cleaned and enriched data into a queryable format;
5. Data Analysis – performing bibliometric and network analyses (e.g. co-citation, co-authorship, thematic mapping).

A separate OSF component will be created for each stage.
Each component will include:
- A detailed protocol or preregistration for that stage;
- A link to the corresponding GitHub repository (for code and sample datasets);
- The associated Zenodo DOI (for archived releases);
- A small sample dataset (first 100 records) to illustrate data structure and format.

This modular structure ensures that every step of the research process — from retrieval to analysis — is independently documented, citable, and verifiable, consistent with best practices in open and reproducible research.

# FIRST COMPONENT: Data Source and Retrieval Plan

## OpenAlex as the database for retrieve PA records

### Why OpenAlex is a Suitable and Reliable Source for Bibliometric Analyses

OpenAlex is a non-profit, open, and continuously expanding scholarly database built on an entity-based structure connecting works, authors, institutions, sources, and funders (Priem et al., 2022).
Developed as the continuation and expansion of the Microsoft Academic Graph—except for patents (Culbert et al. 2025)—it provides free programmatic access to bibliographic metadata.

### Coverage and Comparative Performance

A growing body of studies positions OpenAlex as a strong alternative to traditional proprietary databases.
Alperin et al. (2024) list numerous works already using OpenAlex for bibliometric, altmetric, and scoping-review purposes. Their comparative analysis shows that OpenAlex outperforms Scopus in coverage while presenting minor weaknesses in metadata completeness—such as publication dates, volume and issue numbers, page information, abstracts, author names, or institutional affiliations. They conclude that OpenAlex can already serve as a reliable basis for some forms of bibliometric analysis.
Thelwall and Jiang (2025) similarly find that OpenAlex delivers citation counts comparable to—or in some fields greater than—Scopus, confirming its suitability for bibliometric and evaluative research.Their results suggest that Scopus may still maintain slightly higher precision in citation data owing to its maturity, but OpenAlex achieves broader document coverage.

Culbert et al. (2025) provide further empirical validation through an internal coverage comparison, measuring the proportion of cited references in a dataset that are themselves indexed as source items. They demonstrate that OpenAlex performs comparably to WoS and Scopus in this respect and can thus be used as a credible substitute for large-scale analyses. They note, however, that because OpenAlex records only source references—citations to works already indexed—it may underestimate total citation counts relative to databases containing “non-source references” (final section).

Vieira and Leta (2024) reinforce the importance of coverage measures such as overlaps (the proportion of items shared across databases) to evaluate database comprehensiveness. This methodological logic underpins much of Culbert et al.’s work, as they argue that OpenAlex performs well when assessed via internal coverage but still differs from Scopus and WoS in document representation.

### Metadata Quality and Known Limitations

While generally robust, OpenAlex metadata still present limitations acknowledged by several studies.
Alperin et al. (2024) identify issues in the correctness of bibliographic information and document-type classification. Thelwall and Jiang (2025) also note the misclassification of editorial contributions as journal articles, which may distort field-normalised citation metrics. Rodrigues et al. (2025) discuss errors that can prevent citation matching—such as inconsistent or incorrect DOIs, author names, or journal titles. They warn that relying on a single source can produce incomplete data, either because of coverage limitations or citation misidentifications.
Delgado-Quirós and Ortega (2024) highlight similar concerns but point out that quality assessment must go beyond quantity, considering the accuracy of content and metadata. They report that OpenAlex performs well on overall reliability, though early versions showed losses in bibliographic details such as volume or page number. Nonetheless, since its 2023 release, OpenAlex has undergone multiple rounds of improvement documented in its public release notes (OurResearch, 2025).

### Transparency, Accessibility, and Open-Science Alignment

One of OpenAlex’s strongest assets is its non-profit and open-access orientation. Alperin et al. (2024) stress that its open data and source code make it a transparent infrastructure. Haunschild and Bornmann (2024) praise its free accessibility and replicability, describing OpenAlex as essential for building transparent and reusable science maps. Scheidsteger et al. (2025) situate OpenAlex within a broader movement of open research infrastructures (ORIDs), arguing that transparent, auditable databases are vital for democratising research evaluation and ensuring that assessments can be reproduced by anyone, not only by those with access to proprietary systems.

### Suitability for the Present Project

Given these characteristics, OpenAlex is an appropriate and reliable choice for the Public Administration Snapshot project.
1. Comprehensive coverage: Alperin et al. (2024) show that it functions as a superset of Scopus, ensuring a wide inclusion of Public Administration works.
2. Transparent infrastructure: its open API and documented updates enable reproducible workflows (Alperin et al. 2024; Haunschild & Bornmann 2024).
3. Proven utility: multiple comparative studies (Culbert et al. 2025; Thelwall & Jiang 2025; Scheidsteger et al. 2025) confirm its growing suitability for bibliometric and evaluative research.
At the same time, metadata inconsistencies (Alperin et al. 2024; Delgado-Quirós & Ortega 2024), misclassifications (Thelwall & Jiang 2025), and missing references (Culbert et al. 2025) require careful handling through transparent cleaning and disambiguation, which this project explicitly documents. However, the new release of Walden, the full rewrite of OpenAlex, seems promising for what concern metadata overall quality and precision. 

### Conclusion

Across the literature, OpenAlex emerges as a credible, improving, and ethically aligned bibliometric data source. Its combination of broad coverage, open accessibility, and commitment to continuous improvement supports its use as a foundation for reproducible research. By acknowledging its limitations and applying systematic data-cleaning procedures, projects such as this one can leverage OpenAlex’s openness while ensuring scientific rigour and traceability.

## Data retrieval from OpenAlex

### Boundaries of the records
- **Public Administration boundaries**: PA FIELD JCR SSCI AND ESCI -> I HAVE TO DEDICATE TO THIS A LOT OF ATTENTION, USING BOURDIEU, SCHIRONE, FORTUNATO ET AL. 2018, KHUN AND ETC.
For this part, I should not start by taking for granted that journals are the best way. However, Journals could be considered a good proxy to gain insights about the intellectual and social organisation of a field. The two adjectives intellectual and social could be referred to the concept of scientific authority/competence in which technical capacity and social power (understood as the legitimacy to speak and act for what concerns the scientific matter of a discipline or a field)
Some experts input? What do you think?
Indeed, I could  provide three different reasons for which JCR is the perfect one: the theoretical one, using Bourdieu, etc.; previous approaches, using what other scholars have done in the past, some experts input (not necessarily a Delphi study but something easier and more reasonable)
- **Coverage period**: 1980-2024. Generally, bibliographic information started to be more reliable from 1980 onwards (FIND ABSOLUTELY THE REFERENCE HERE). I have excluded 2025 to mitigate risks of recency-related inaccuracies in the data compilation or recall, whether arising from editors or from OpenAlex. (ADD OTHER EXPLANATION IF POSSIBLE)
- **Document types**: through the API, it is possible to choose among the following work types: article; book chapter; dataset; pre-print; dissertation; book; review; paratext; other; libguides; letter; reference-entry; report; peer-review; editorial; erratum; standard; grant; supplementary materials; retraction; book-section; software; database; report component.
    For consistency matters, this database will retrieve exclusively works labelled as articles. (PROVIDE AN EXPLANATION HERE AND DEFINE WHAT "CONSISTENCY MATTERS" MEANS)
- **Language selection**: THe JCR PA SSCI and ESCI categories mostly consist into English-written journals. However, there are a few exceptions of Spanish or French-written journals which will be included, following the Leiden Manifesto recommendations of building metrics inclusive of high-quality non-English literature.
- **Metadata selection**: The OpenAlex dataset is built around *entities*. The first retrieval will be built around the *Work object*, which is focused on all different kinds of scholarly documents— journal articles in our case. The following list enucleates the different metadata selected for following analyses (ADJUST LAST PART)
    **WORK OBJECT**
    1. abstract_inverted_index. Due to legal constraints, OpenAlex is stored as an inverted index (SEE IF HOW TO DOWNLOAD IT AND IF I HAVE TO USE PYALEX OR OTHER CLIENT LIBRARIES AS IN "HOW TO USE API" SECTION OF THE OPENALEX DOCUMENTATION)
    2. biblio. This parameter gives the possibility of obtaining the volume, issue, first page, and last page of a work object
    3. cited_by_count. The number of citations of a work. This would be updated each year or at any other regular interval (ADJUST THIS PART)
    4. DOI. In the case that a work has more than one DOI, like a DOI for a preprint version of a work, OpenAlex refers to the DOI for the published work
    5. grants. This parameter gives several information about the possible funding of a work object, including funder and the award ID if available. OpenAlex, however, admits the limited extension of this info across the database
    6. id. It indicates the OpenAlex ID for this work. This information is fundamental to create the future SQL database
    7. is_paratext. This parameter indicates if a work is a paratext, namely front cover, back cover, table of contents, editorial board listing, issue information, masthead. This would be beneificial for the data cleaning phase, in which all the entries is_paratext: true will be automatically excluded
    8. Language. The downside of this parameter is that it is calibrated on metadata language and not full text. So, if the abstract is in English but the full-text is in French, the parameter will report "English"
    9. open_access. Several info about the access status of the work, potentially leading also to the oa_url
    10. publication_year.
    11. referenced_works. Instead of using shortened version of references, such as Web of Science, OpenAlex provides the OpenAlex ID corresponding to the works cited.
    12. title.
    13. type. (PERSONALLY I AM NOT SURE, SINCE I WILL DOWNLOAD ONLY ARTICLES FROM SPECIFIC JOURNALS, SO IT SHOULD NOT BE POSSIBLE TO HAVE ANY RECORD WHICH IS NOT AN ARTICLE AND NOT COMING FROM A SPECIFIC JOURNAL)
    14. oa_url. It could be or the direct link to the PDF or to the landing page that links to the free PDF
    **AUTHORSHIP OBJECT**
    Within the work object, there are specific parameters dedicated to the info about authors. They are different from the ones in the **AUTHOR OBEJCT** which will be downloaded in a further retrieval once the initial snapshot focused on works will be completed. As far as concerns the work object, the authorship object metadata included will be:
    15. author. For the work object, we could obtain a dehydrated Author object. It will include the OpenAlex ID of the author, the name of the author, and their ORCID. These IDs will be fundamental for a further retrieval from OpenAlex based on the IDs of the specific authors, collecting info beyond the Public Administration field identified through its articles.
    16. countries. Technically, this parameter will be obtained once the Institution object related retrieval will be done. However, it is not based just on the institution of the author, but on a combination of parsing raw affiliation strings. In this sense, it could be reported a country affiliation even if OpenAlex doesn't have a specific institution affiliation
    17. institutions. This parameter will return the institutional affiliations claimed by the author in the context of a specific work. The metadata will be built as a dehydrated Institutions objects. As with the author parameter(number 15), this information will be used for a further retrieval from OpenAlex based on the IDs of the institutions.

### Data retrieval
- Records were retrieved at the journal level, with OpenAlex IDs used to ensure precise source identification. Initially, the full list of Public Administration journals indexed in JCR SSCI and ESCI was exported (see PA_JCR_SSCI_ESCI.xlsx). Subsequently, the corresponding OpenAlex IDs for each journal were identified and employed in the search query (see PYTHON SCRIPT), to prevent the retrieval of records from journals with similar or potentially confounding titles.
- The retrieval script will query the OpenAlex API for all Works in under the journals IDs in the PA_JCR_SSCI_ESCI.xlsc, extracting works according to filters and metadata as outlined in the "Boundaries of the records" section. The definitive script will be released on GitHub once debugging and validation are complete.

**Retrieval method**:
- Python script: 01_download_openalex.py (available on GitHub)
- Queries built around ISSNs of relevant journals and/or OpenAlex concept IDs.
- API requests documented in docs/methodology.md.
- Raw data stored in data/raw/ with JSON and CSV exports.
**Planned outputs**:
- Full metadata CSV for all retrieved records;
- Log of API queries and rate-limit handling;
- Summary statistics of retrieval coverage.

# SECOND COMPONENT: Data Cleaning and Integration

**Scripts and logic**:
- "02_clean_metadata.py": field normalisation (titles, authors, DOIs, journals, institutions).
- Deduplication based on DOI, title, and OpenAlex ID.
- Handling of missing fields (e.g., missing DOIs or years).
- Country and institution standardisation using OpenAlex affiliation data.
**Planned outputs**:
- Cleaned CSV files in data/cleaned/;
- Harmonised field list in docs/data_dictionary.md;
- Summary report of missing/invalid entries.

# THIRD COMPONENT: Data Enrichment
- Downloading author and institution object from OpenAlex, using OpenAlex ID as foreign keys for integrating in a SQL database afterwards
- Download of all the references of the work object database
- Gender information
- Other info?

# FOURTH COMPONENT: SQL Database creation

# FIFHT COMPONENT: Data Analysis

Planned analyses:
Descriptive bibliometrics (yearly trends, document types, country shares);

Co-authorship and institutional collaboration networks;

Keyword co-occurrence and thematic mapping;

Citation network overview (using OpenAlex references);

Future extension: topic modelling and temporal evolution analysis.

Software tools:

Python (pandas, networkx, matplotlib, rapidfuzz);

R (bibliometrix, VOSviewer).

Output files:

Tables and network exports (data/outputs/);

Visualisation notebooks (notebooks/ folder on GitHub).

7. Planned Transparency and Reproducibility Measures
Platform	Purpose
GitHub	Version-controlled scripts and workflow documentation (link
)
Zenodo	DOI-minted, archived releases of datasets and code
OSF	Central project hub and preregistration (this page)
ORCID	Researcher identity linkage (link
)

Licences:

MIT for code;

CC-BY 4.0 for documentation and data.

8. Expected Limitations

OpenAlex metadata may contain incomplete affiliation or reference data for certain periods.

Data cleaning rules may evolve as new metadata fields become available.

Topic boundaries of “Public Administration” may require adjustment after initial inspection.

These limitations will be handled transparently in future updates, with clear change logs and new OSF components where appropriate.

9. Future Updates and Change Management

Given the evolving nature of this project, changes may occur in:

Data scope (e.g. inclusion of new journals or document types);

Cleaning logic (e.g. updated DOI or title harmonisation);

Analytical methods (e.g. addition of topic modelling).

Any such modifications will be recorded as:

New OSF components or new registrations, each with their own timestamp;

Linked to corresponding Zenodo releases (archived versions);

Accompanied by a CHANGELOG_vX.md explaining the updates.

10. References and Related Materials

OpenAlex documentation: https://docs.openalex.org/

OSF project: https://osf.io/xxxx/

Zenodo DOI (for v1.0 release): https://doi.org/10.5281/zenodo.xxxxxxx

GitHub repository: https://github.com/fulvioscognamiglio/openalex-pa-snapshot

11. Registration Notes (optional reflection field)

This preregistration represents the first stage of the Public Administration Snapshot project.
It is intended as a transparent record of the data retrieval and design phase.
Later analytical or methodological developments will be documented through additional OSF components or new preregistrations linked to this one.

✅ Summary: how this helps you stay flexible
Situation	What to do in OSF
Minor change (e.g. tweak in code or query)	Update GitHub + note in changelog
Moderate change (e.g. expand scope, add analysis)	Create a new OSF component
Major change (e.g. reframe study design)	Create a new preregistration linked to the previous one

This layered approach means your project stays transparent, traceable, and credible, while still allowing you to evolve it naturally.

# References

- Alperin, J. P., Portenoy, J., Demes, K., Larivière, V., & Haustein, S. (2024). An analysis of the suitability of OpenAlex for bibliometric analyses. arXiv preprint arXiv:2404.17663.
- Culbert, J. H., Hobert, A., Jahn, N., Haupka, N., Schmidt, M., Donner, P., & Mayr, P. (2025). Reference coverage analysis of OpenAlex compared to Web of Science and Scopus. Scientometrics, 130(4), 2475-2492.
- Delgado-Quirós, L., & Ortega, J. L. (2024). Completeness degree of publication metadata in eight free-access scholarly databases. Quantitative Science Studies, 5(1), 31-49.
- Haunschild, R., & Bornmann, L. (2024). The use of OpenAlex to produce meaningful bibliometric global overlay maps of science on the individual, institutional, and national levels. PloS one, 19(12), e0308041.
- Hicks, D., Wouters, P., Waltman, L., De Rijcke, S., & Rafols, I. (2015). Bibliometrics: the Leiden Manifesto for research metrics. Nature, 520(7548), 429-431.
- OurResearch. (2025). OpenAlex release notes – standard format (data dumps) [Computer software documentation]. GitHub. https://github.com/ourresearch/openalex-guts/blob/main/files-for-datadumps/standard-format/RELEASE_NOTES.txt
- Priem, J., Piwowar, H., & Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. arXiv preprint arXiv:2205.01833.
- Rodrigues, D., Lopes, A., & Batista, F. (2025). Detecting incoherent citation data among three bibliometric platforms: OpenAlex, Scopus and Web of Science. Journal of Information Science, 01655515251330579.
- Scheidsteger, T., & Haunschild, R. (2023). Which of the metadata with relevance for bibliometrics are the same and which are different when switching from Microsoft Academic Graph to OpenAlex?. Profesional de la información, 32(2).
- Scheidsteger, T., Haunschild, R., & Bornmann, L. (2025). How similar are field-normalized citation impact scores obtained from OpenAlex and three popular commercial databases? An empirical comparison based on large German universities. Scientometrics, 1-33.
- Thelwall, M., & Jiang, X. (2025). Is OpenAlex suitable for research quality evaluation and which citation indicator is best?. Journal of the Association for Information Science and Technology.
- Vieira, G. A., & Leta, J. (2024). biblioverlap: an R package for document matching across bibliographic datasets. Scientometrics, 129(7), 4513-4527.
- Willemin, S. (2025). Two definitions to characterize the relations between columns in a given scholarly metadata data set. Quantitative Science Studies, 6, 546-566.