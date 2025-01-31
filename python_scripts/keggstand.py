import copy
import gzip
import io
import logging
import pickle
from pathlib import Path
from collections import OrderedDict
from itertools import product
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import requests
import tqdm
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


__all__ = ["EntryID", "Entries", "Entry", "Relation", "Kegg", "KeggPathway"]


logger = logging.getLogger("kegg-stand")


class Paths:
    kegg_cache: Path = Path("~/kegg.cache.gz").expanduser()


EntryID = str
Entries = Dict[EntryID, "Entry"]


class Entry:
    def __init__(self, eid: str, accessions: List[str], entry_type: str):
        if isinstance(accessions, str):
            accessions = accessions.split(" ")
        self.eid = eid
        self.accessions = accessions
        self.entry_type = entry_type

    def __repr__(self) -> str:
        return str(
            dict(
                eid=self.eid,
                accessions=self.accessions,
                entry_type=self.entry_type,
            )
        )


class Relation:
    def __init__(
        self, source: Entry, target: Entry, category: str, labels: List[str]
    ):
        self.source: Entry = source
        self.target: Entry = target
        self.category: str = category
        self.labels: List[str] = labels

    def __repr__(self) -> str:
        return str(
            dict(
                source=self.source.eid,
                target=self.target.eid,
                category=self.category,
                labels=self.labels,
            )
        )


class KeggPathway:
    def __init__(self, xml: str):
        self.root: BeautifulSoup = BeautifulSoup(xml, features="xml")

    def __repr__(self) -> str:
        return str(self.root)

    @property
    def entries(self) -> Entries:
        entries: Entries = {}
        for entry in self.root.find_all("entry"):
            kegg_id = entry["id"]
            accessions = entry["name"].split(" ")
            entry_type = entry["type"]
            entry = Entry(
                eid=kegg_id, accessions=accessions, entry_type=entry_type
            )
            entries[kegg_id] = entry
        return entries

    @property
    def relations(self) -> List[Relation]:
        relations: List[Relation] = []
        entries: Entries = self.entries
        for relation in self.root.find_all("relation"):
            subtypes: List[Dict] = relation.find_all("subtype")
            source: Entry = entries[relation["entry1"]]
            target: Entry = entries[relation["entry2"]]
            category: str = relation["type"]
            labels: List[str] = [st["name"] for st in subtypes]
            relations.append(
                Relation(
                    source=source,
                    target=target,
                    category=category,
                    labels=labels,
                )
            )
        return relations

    @property
    def interactions(self) -> pd.DataFrame:
        data: Dict[str, List[Any]] = {"source": [], "target": [], "label": []}
        include_categories = ("pprel",)
        for relation in self.relations:
            if relation.category.lower() not in include_categories:
                continue
            if relation.source.entry_type.lower() not in ("gene",):
                continue
            if relation.target.entry_type.lower() not in ("gene",):
                continue

            combinations = product(
                relation.source.accessions, relation.target.accessions
            )
            for s, t in combinations:
                for label in relation.labels:
                    data["source"].append(s)
                    data["target"].append(t)
                    data["label"].append(label)

        return (
            pd.DataFrame(data=data, columns=["source", "target", "label"])
            .drop_duplicates(subset=None, keep="first", inplace=False)
            .dropna(axis=0, how="any", inplace=False)
        )


class Kegg:
    """
    Simple wrapper for KEGG's API.

    Attributes
    ----------
        organisms : str
            KEGG three letter organism code.
    """

    def __init__(
        self,
        base: str = "http://rest.kegg.jp/",
        use_cache: bool = False,
        max_retries: int = 5,
    ):
        self.base = base
        self.cache: Dict[str, Any] = {}
        self.use_cache = use_cache
        if self.use_cache:
            self.load_cache()

        # Create re-try handler and mount it to the session using the base
        # url as the prefix
        self.session = requests.Session()
        retries = Retry(total=max_retries, respect_retry_after_header=True)
        self.session.mount(self.base, HTTPAdapter(max_retries=retries))

    def delete_cache(self):
        self.cache = {}
        self.save_cache()

    def load_cache(self):
        if Paths.kegg_cache.exists():
            self.cache = pickle.load(gzip.open(Paths.kegg_cache, "rb"))

    def save_cache(self, overwrite: bool = False):
        if not self.use_cache:
            # Bypass saving if use has requested not to use cache.
            return

        if overwrite:
            pickle.dump(self.cache, gzip.open(Paths.kegg_cache, "wb"))
        else:
            existing = (
                pickle.load(gzip.open(Paths.kegg_cache, "rb"))
                if Paths.kegg_cache.exists()
                else {}
            )
            # Updates existing cache instead of over-writting
            existing.update(self.cache)
            pickle.dump(existing, gzip.open(Paths.kegg_cache, "wb"))

    def _url_builder(self, operation: str, arguments: Union[str, List[str]]):
        if isinstance(arguments, str):
            arguments = [arguments]
        if not arguments:
            raise ValueError("At least one argument is required.")
        return "{}{}/{}/".format(self.base, operation, "/".join(arguments))

    @staticmethod
    def parse_json(response: requests.Response):
        # Raise error if response failed. Only raised for error codes.
        response.raise_for_status()
        return response.json()

    @staticmethod
    def parse_dataframe(
        response: requests.Response,
        delimiter: str = "\t",
        header: Optional[List[int]] = None,
        columns: Optional[List[str]] = None,
    ):
        # Raise error if response failed. Only raised for error codes.
        response.raise_for_status()
        handle = io.StringIO(response.content.decode())

        # Use header to specify column names if defined. Otherwise use
        # user-specifed columns.
        if header:
            return pd.read_csv(handle, delimiter=delimiter, header=header)
        elif columns:
            return pd.read_csv(handle, delimiter=delimiter, names=columns)
        else:
            return pd.read_csv(handle, delimiter=delimiter, header=None)

    def get(self, url: str) -> requests.Response:
        response: requests.Response = self.session.get(url)
        if not response.ok:
            logger.error(f"{response.content.decode()}")
            response.raise_for_status()
        return response

    @property
    def organisms(self) -> pd.DataFrame:
        url = self._url_builder("list", "organism")

        if url in self.cache:
            return self.cache[url]

        organisms: pd.DataFrame = self.parse_dataframe(
            self.get(url), columns=["accession", "code", "name", "taxonomy"]
        )
        self.cache[url] = organisms
        self.save_cache()

        return organisms

    def pathways(self, organism: str) -> pd.DataFrame:
        url: str = self._url_builder("list", ["pathway", organism])

        if url in self.cache:
            return self.cache[url]

        pathways: pd.DataFrame = self.parse_dataframe(
            self.get(url), columns=["accession", "name"]
        )
        self.cache[url] = pathways
        self.save_cache()

        return pathways

    def genes(self, organism: str) -> pd.DataFrame:
        url = self._url_builder("list", organism)

        if url in self.cache:
            return self.cache[url]

        genes: pd.DataFrame = self.parse_dataframe(
            self.get(url), columns=["accession", "names"]
        )
        self.cache[url] = genes
        self.save_cache()

        return genes

    def gene_detail(self, accession: str) -> str:
        url = self._url_builder("get", accession)

        if url in self.cache:
            return self.cache[url]

        detail: str = self.get(url).content.decode()
        self.cache[url] = detail
        self.save_cache()

        return detail

    def pathway_detail(self, accession: str) -> KeggPathway:
        # Remove 'path:' prefix if present.
        url = self._url_builder("get", [accession.split(":")[-1], "kgml"])

        if url in self.cache:
            response_data = self.cache[url]
        else:
            response_data = self.get(url).content.decode()
            self.cache[url] = response_data
            self.save_cache()

        return KeggPathway(xml=response_data)

    def parse_all_pathways(
        self, organism: str, verbose: bool = False
    ) -> List[KeggPathway]:
        path_ids: List[str] = list(self.pathways(organism)["accession"])

        if verbose:
            logger.info(
                f"Downloading and parsing {len(path_ids)} '{organism}' "
                f"pathways."
            )
            path_ids = tqdm.tqdm(path_ids, total=len(path_ids))

        return [self.pathway_detail(path_id) for path_id in path_ids]

    def convert(
        self, source: str = "hsa", destination: str = "uniprot"
    ) -> Dict[str, List[str]]:
        url = self._url_builder("conv", [source, destination])

        if url in self.cache:
            return self.cache[url]

        df: pd.DataFrame = self.parse_dataframe(self.get(url))
        mapping: Dict[str, List[str]] = {}
        for row in df.to_dict("records"):
            # KEGG API is structured as destination first then source.
            dst, src = row.values()
            if source != "hsa":
                src = src.split(":")[-1]
            if destination != "hsa":
                dst = dst.split(":")[-1]

            if src in mapping:
                mapping[src].append(dst)
            else:
                mapping[src] = [dst]

        self.cache[url] = mapping
        self.save_cache()

        return mapping
