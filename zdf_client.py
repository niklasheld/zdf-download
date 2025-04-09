from dataclasses import dataclass
import requests
import re
import json
from dateutil import parser


@dataclass
class ZDFEpisode:
    title: str
    sharing_url: str
    editorial_date: str


class ZDFClient():

    def __get_api_key(self):
        url = "https://www.zdf.de"
        response = requests.get(url)
        pattern = r'\\"apiToken\\":\\"([^\\"]+)\\"'
        match = re.search(pattern, response.text)
        if match:
            return match.group(1)
        else:
            raise ValueError("Unable to get API key from ZDF website.")

    def get_episodes(self, canonical_id: str) -> list[ZDFEpisode]:
        result = []

        api_key = self.__get_api_key()

        extensions = {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "9412a0f4ac55dc37d46975d461ec64bfd14380d815df843a1492348f77b5c99a"
            }
        }

        variables = {
            "seasonIndex": 0,
            "episodesPageSize": 24,
            "canonical": canonical_id,
            "sortBy": [
                {
                    "field": "EDITORIAL_DATE",
                    "direction": "DESC"
                }
            ]
        }

        r = requests.get(
            url="https://api.zdf.de/graphql", 
            params={
                "extensions": json.dumps(extensions),
                "variables": json.dumps(variables)
            },
            headers={
                "content-type": "application/json",
                "api-auth": f"Bearer {api_key}"
            }
        )

        if r.status_code == 200:
            data = r.json()
            episodes = data.get("data", {}).get("smartCollectionByCanonical", {}).get("seasons", {}).get("nodes", [{}])[0].get("episodes", {}).get("nodes", [])
            for episode in episodes:
                result.append(ZDFEpisode(
                    title=episode.get("title"),
                    sharing_url=episode.get("sharingUrl"),
                    editorial_date=parser.parse(episode.get("editorialDate"))
                ))
        else:
            raise ValueError(f"Error fetching episodes: {r.status_code} - {r.text}")
        return result
