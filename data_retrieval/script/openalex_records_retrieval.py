import requests
import time
import os
import csv

# --- CONFIGURATION ---
mailto = "fulvio.scognamiglio@lsbu.ac.uk"
base_url = "https://api.openalex.org/works"

# Base folder where all TSVs will be saved
output_dir = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data"

# Journals: internal short name + OpenAlex source.id (without the 'id:' prefix)
JOURNALS = [
    {"short_name": "ADMINSOC",   "source_id": "s5465880"},
    {"short_name": "ARPA",       "source_id": "s106702950"},
    {"short_name": "AMMEIDA",    "source_id": "s1035621232"},
    {"short_name": "AJPA",       "source_id": "s128357121"},
    {"short_name": "CANPA",      "source_id": "s71588376"},
    {"short_name": "CANPUB",     "source_id": "s49494758"},
    {"short_name": "CIVSZE",     "source_id": "s1039215795"},
    {"short_name": "CLIMAPOL",   "source_id": "s113876312"},
    {"short_name": "CONTPOL",    "source_id": "s185930956"},
    {"short_name": "CRITPOL",    "source_id": "s70419765"},
    {"short_name": "ENVIPLAN",   "source_id": "s4210204712"},
    {"short_name": "GESPUB",     "source_id": "s163496299"},
    {"short_name": "GOVERNANCE", "source_id": "s62375027"},
    {"short_name": "HUMSERV",    "source_id": "s4210226981"},
    {"short_name": "IPMJ",       "source_id": "s63571029"},
    {"short_name": "IRAS",       "source_id": "s16140064"},
    {"short_name": "JAPP",       "source_id": "s86762183"},
    {"short_name": "CHIGOV",     "source_id": "s4210183829"},
    {"short_name": "JCPA",       "source_id": "s77082647"},
    {"short_name": "JEPP",       "source_id": "s22371039"},
    {"short_name": "JESP",       "source_id": "s187013691"},
    {"short_name": "HOMSEC",     "source_id": "s196738966"},
    {"short_name": "JPAM",       "source_id": "s25370267"},
    {"short_name": "JPART",      "source_id": "s169433491"},
    {"short_name": "JPUBPOL",    "source_id": "s76906069"},
    {"short_name": "JSOCPOL",    "source_id": "s178021067"},
    {"short_name": "LEXLOC",     "source_id": "s4210189277"},
    {"short_name": "LGS",        "source_id": "s171234518"},
    {"short_name": "NONPROF",    "source_id": "s70709366"},
    {"short_name": "POLANDPOL",  "source_id": "s17167983"},
    {"short_name": "POLICYSCI",  "source_id": "s197895017"},
    {"short_name": "POLANDSOC",  "source_id": "s129664799"},
    {"short_name": "POLSTUJOU",  "source_id": "s119514724"},
    {"short_name": "POLSTU",     "source_id": "s114598798"},
    {"short_name": "PUBADM",     "source_id": "s201221823"},
    {"short_name": "PAD",        "source_id": "s189395249"},
    {"short_name": "PAR",        "source_id": "s76877748"},
    {"short_name": "PMR",        "source_id": "s37623806"},
    {"short_name": "PUBMON",     "source_id": "s87681011"},
    {"short_name": "PUBPERF",    "source_id": "s136809933"},
    {"short_name": "PUBPERS",    "source_id": "s38942948"},
    {"short_name": "PPA",        "source_id": "s17185278"},
    {"short_name": "REGULGOV",   "source_id": "s108218269"},
    {"short_name": "REVPOL",     "source_id": "s54913114"},
    {"short_name": "REPPA",      "source_id": "s51277951"},
    {"short_name": "SCIPUB",     "source_id": "s4210168539"},
    {"short_name": "SOCPOL",     "source_id": "s31120751"},
    {"short_name": "TRANSAD",    "source_id": "s2764352865"},
    {"short_name": "EARTHGOV",   "source_id": "s4210220330"},
    {"short_name": "PERSPECTMAN","source_id": "s2735938357"},
    {"short_name": "BEHAVPUB",   "source_id": "s4210205184"},
    {"short_name": "EURPOLAN",   "source_id": "s4210228320"},
    {"short_name": "DATAPOL",    "source_id": "s197895017"},
    {"short_name": "POLICYDES",  "source_id": "s4210224919"},
    {"short_name": "JPUBBUD",    "source_id": "s2912564958"},
    {"short_name": "IJPSM",      "source_id": "s90998793"},
    {"short_name": "JPUBPRO",    "source_id": "s2913448381"},
    {"short_name": "GLOBPUB",    "source_id": "s4210169212"},
    {"short_name": "IJPM",       "source_id": "s39541053"},
    {"short_name": "ASIAPAC",    "source_id": "s4210170541"},
    {"short_name": "JAFFED",     "source_id": "s2914543899"},
    {"short_name": "RISKHAZ",    "source_id": "s8264181"},
    {"short_name": "JAFF",       "source_id": "s4210184645"},
    {"short_name": "EURJSOC",    "source_id": "s205798773"},
    {"short_name": "PUBORG",     "source_id": "s162137778"},
    {"short_name": "IJPL",       "source_id": "s4210232233"},
    {"short_name": "NONPROFPOL", "source_id": "s4210205114"},
    {"short_name": "CENTEUR",    "source_id": "s4210204642"},
    {"short_name": "PUBINTEGR",  "source_id": "s132726681"},
    {"short_name": "NISPACEEJ",  "source_id": "s13135386"},
    {"short_name": "PUBWORK",    "source_id": "s62940521"},
    {"short_name": "PUBBUD",     "source_id": "s184729184"},
    {"short_name": "CHINPUB",    "source_id": "s4210231999"},
    {"short_name": "INTSOC",     "source_id": "s134782007"},
    {"short_name": "JPUBNON",    "source_id": "s4210180838"},
    {"short_name": "PUPAS",      "source_id": "s4210225381"},
    {"short_name": "REVADM",     "source_id": "s4210228912"},
    {"short_name": "COMMONW",    "source_id": "s2764345097"},
    {"short_name": "ELECTRGOV",  "source_id": "s23830393"},
    {"short_name": "CANNON",     "source_id": "s2737149045"},
    {"short_name": "REVIBE",     "source_id": "s4210235114"},
    {"short_name": "CROATCOMP",  "source_id": "s4210177412"},
    {"short_name": "CADGEST",    "source_id": "s4210240407"},
    {"short_name": "REVGEST",    "source_id": "s4210209537"},
    {"short_name": "REVSERV",    "source_id": "s4210181490"},
    {"short_name": "ADMIN",      "source_id": "s4210204991"},
    {"short_name": "OPERA",      "source_id": "s4210173380"},
    {"short_name": "ADMPUB",     "source_id": "s2736899031"},
]


def decode_abstract(abstract_inverted_index):
    """Reconstruct abstract string from OpenAlex's abstract_inverted_index."""
    if not abstract_inverted_index or not isinstance(abstract_inverted_index, dict):
        return "N/A"

    pos2word = {}
    try:
        for word, positions in abstract_inverted_index.items():
            for p in positions:
                pos2word[p] = word
        words = [pos2word[i] for i in sorted(pos2word.keys())]
        text = " ".join(words)
    except Exception:
        return "N/A"

    text = " ".join(text.split()).strip()
    return text if text else "N/A"


def fetch_works_for_journal(source_id: str):
    """Fetch all works for a given OpenAlex source.id (journal)."""
    filter_str = (
        f"primary_location.source.id:{source_id},"
        "type:article|review,"
        "from_publication_date:1980-01-01,"
        "to_publication_date:2024-12-31"
    )

    params = {
        "filter": filter_str,
        "per-page": 100,
        "cursor": "*",
        "mailto": mailto,
    }

    all_works = []
    print(f"\n🔍 Downloading records from OpenAlex for source_id={source_id}…")

    while True:
        response = requests.get(base_url, params=params)
        print(f"Status: {response.status_code} | URL: {response.url}")

        if response.status_code != 200:
            print("❌ Error:", response.text)
            break

        data = response.json()
        works = data.get("results", [])
        all_works.extend(works)
        print(f"→ Fetched {len(works)}, total so far: {len(all_works)}")

        next_cursor = data["meta"].get("next_cursor")
        if not next_cursor:
            break

        params["cursor"] = next_cursor
        time.sleep(1)

    print(f"✅ Total records fetched for {source_id}: {len(all_works)}")
    return all_works


def export_works_to_tsv(works, output_file: str):
    """Export a list of works to a tab-delimited TSV file."""
    headers = [
        "Journal", "Title", "Year", "Type",
        "Is_Paratext", "Language",
        "DOI", "OpenAlex_ID", "Cited_by",
        "OA_Status", "Is_OA", "OA_URL", "OA_Licence",
        "Referenced_Works",
        "Corresponding_Authors", "Corresponding_Institutions",
        "Volume", "Issue", "Pages",
        "Grants", "Authors", "Abstract"
    ]

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(headers)

        for work in works:
            authorships = work.get("authorships", [])
            if not authorships:
                continue

            is_paratext = work.get("is_paratext", None)
            language = work.get("language", "N/A")

            oa = work.get("open_access", {}) or {}
            is_oa = oa.get("is_oa", None)
            oa_status = oa.get("oa_status", "N/A")
            oa_url = oa.get("oa_url", "N/A")
            oa_licence = oa.get("license", "N/A")

            refs = work.get("referenced_works", []) or []
            referenced_works_str = " | ".join(refs) if refs else "N/A"

            abstract_txt = decode_abstract(work.get("abstract_inverted_index"))
            abstract_txt = abstract_txt.replace("\t", " ").replace("\r", " ").replace("\n", " ")

            author_entries = []
            for a in authorships:
                author = a.get("author", {}) or {}
                institutions = a.get("institutions", []) or []
                affiliations = a.get("affiliations", []) or []
                countries = a.get("countries", []) or []

                inst_parts = []
                for inst in institutions:
                    inst_parts.append(
                        f"{inst.get('display_name', 'N/A')} "
                        f"### ID: {inst.get('id', 'N/A')} "
                        f"### ROR: {inst.get('ror', 'N/A')} "
                        f"### Type: {inst.get('type', 'N/A')}"
                    )
                inst_str = " || ".join(inst_parts) if inst_parts else "N/A"

                aff_str = (
                    "#TAB#".join(aff.get("raw_affiliation_string", "") for aff in affiliations)
                    or "N/A"
                )

                author_entry = (
                    f"{author.get('display_name', 'N/A')} ({a.get('raw_author_name', 'N/A')}); "
                    f"Author_ID: {author.get('id', 'N/A')}; "
                    f"ORCID: {author.get('orcid') or 'None'}; "
                    f"Position: {a.get('author_position', 'N/A')}; "
                    f"Countries: {', '.join(countries) or 'N/A'}; "
                    f"Institutions: {inst_str}; "
                    f"Affiliations: {aff_str}"
                )
                author_entries.append(author_entry)

            biblio = work.get("biblio", {}) or {}
            grants = work.get("grants", []) or []
            grant_lines = [
                f"{g.get('funder_display_name', 'Unknown')} (ID: {g.get('award_id', 'Unknown')})"
                for g in grants
            ]

            journal_name = (
                work.get("primary_location", {})
                    .get("source", {})
                    .get("display_name", "N/A")
            )

            writer.writerow([
                journal_name,
                work.get("title", "N/A"),
                work.get("publication_year", "N/A"),
                work.get("type", "N/A"),
                is_paratext,
                language,
                work.get("doi", "N/A"),
                work.get("id", "N/A"),
                work.get("cited_by_count", 0),
                oa_status,
                is_oa,
                oa_url,
                oa_licence,
                referenced_works_str,
                ", ".join(work.get("corresponding_author_ids", []) or ["N/A"]),
                ", ".join(work.get("corresponding_institution_ids", []) or ["N/A"]),
                biblio.get("volume", "N/A"),
                biblio.get("issue", "N/A"),
                f"{biblio.get('first_page', 'N/A')}-{biblio.get('last_page', 'N/A')}",
                "; ".join(grant_lines) or "N/A",
                " | ".join(author_entries),
                abstract_txt
            ])

    print(f"📁 Saved TSV to: {os.path.abspath(output_file)}")


if __name__ == "__main__":
    for j in JOURNALS:
        short = j["short_name"]
        source_id = j["source_id"]

        print("\n============================")
        print(f"📚 Processing journal: {short} (source_id={source_id})")
        print("============================")

        works = fetch_works_for_journal(source_id)

        if not works:
            print(f"⚠ No works retrieved for {short} ({source_id}) – skipping file export.")
            continue

        out_path = os.path.join(output_dir, f"{short}_openalex.tsv")
        export_works_to_tsv(works, out_path)
