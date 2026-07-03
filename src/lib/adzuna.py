"""
adzuna.py
=========
Client for the Adzuna Jobs API.

Docs: https://api.adzuna.com/v1/doc

Quick reference:
  search(what, where, domain) → list of job dicts
  get_categories()            → list of valid category tags

Example:
  client = AdzunaClient()
  jobs = client.search(what="mental health counselor", where="Connecticut")
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"
COUNTRY         = "us"


class AdzunaClient:

    def __init__(self):
        app_id  = os.getenv("ADZUNA_APP_ID")
        app_key = os.getenv("ADZUNA_APP_KEY")

        if not app_id or not app_key:
            raise ValueError("ADZUNA_APP_ID and ADZUNA_APP_KEY must be set in .env")

        self.app_id  = app_id
        self.app_key = app_key
        self.base    = f"{ADZUNA_BASE_URL}/{COUNTRY}"

    def search(
        self,
        what: str,
        where: str = "",
        results_per_page: int = 20,
    ) -> list[dict]:
        """
        Search for jobs by keyword and location.

        Args:
            what:             job title or keywords e.g. "mental health counselor"
            where:            location e.g. "Connecticut" or "Hartford CT"
            results_per_page: max results to return (max 50)
            page:             page number for pagination
            sort_by:          "date" | "salary" | "relevance"

        Returns:
            list of job dicts with keys:
              id, title, company, location, description,
              salary_min, salary_max, redirect_url, created
        """
        params = {
            "app_id":           self.app_id,
            "app_key":          self.app_key,
            "results_per_page": str(results_per_page),
            "what": what
        }

        if where:
            params["where"] = where

        url      = f"{self.base}/search"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        return self._normalize(data.get("results", []))

    def get_categories(self) -> list[dict]:
        """
        Returns all valid Adzuna job categories.
        Useful for filtering by category tag.
        """
        params = {
            "app_id":       self.app_id,
            "app_key":      self.app_key,
        }
        
        url      = f"{self.base}/categories"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        return response.json().get("results", [])

    def _normalize(self, results: list[dict]) -> list[dict]:
        """
        Normalize raw Adzuna results into a clean consistent shape.
        Strips Adzuna-specific nesting and fills missing fields with None.
        """
        normalized = []

        for job in results:
            normalized.append({
                "id":          job.get("id"),
                "title":       job.get("title"),
                "company":     job.get("company", {}).get("display_name"),
                "location":    job.get("location", {}).get("display_name"),
                "description": job.get("description"),
                "salary_min":  job.get("salary_min"),
                "salary_max":  job.get("salary_max"),
                "salary_is_predicted": job.get("salary_is_predicted") == "1",
                "url":         job.get("redirect_url"),
                "created":     job.get("created"),
                "category":    job.get("category", {}).get("label"),
            })

        return normalized