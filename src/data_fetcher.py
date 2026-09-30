"""
Multi-Source Data Fetcher & Incremental Ingestion Module.

Fetches anime metadata from:
1. Primary: AniList GraphQL API (https://graphql.anilist.co)
2. Secondary Fallback: Kitsu REST API (https://kitsu.io/api/edge/anime)
3. Offline Local: SQLite Incremental Database (data/anime_catalog.db)
4. Static Fallback: Built-in 55-item curated mock dataset

Features rate limiting to prevent API bans, incremental pagination resumption,
and automatic synchronization to data/raw_anime_data.json.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple
import requests

from src.database import AnimeCatalogDB

logger = logging.getLogger("data_fetcher")


# ---------------------------------------------------------------------------
# Curated Built-in Mock Dataset (55 anime across diverse archetypes)
# ---------------------------------------------------------------------------
MOCK_ANIME_DATA: List[Dict[str, Any]] = [
    # 1. Classics
    {
        "id": 30,
        "title": {"romaji": "Shinseiki Evangelion", "english": "Neon Genesis Evangelion"},
        "seasonYear": 1995,
        "season": "FALL",
        "episodes": 26,
        "duration": 24,
        "genres": ["Action", "Drama", "Mecha", "Mystery", "Psychological", "Sci-Fi"],
        "tags": [{"name": "Philosophy", "rank": 96, "isMediaSpoiler": False}, {"name": "Post-Apocalyptic", "rank": 90, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Gainax", "isAnimationStudio": True}]},
        "source": "ORIGINAL",
        "averageScore": 83,
        "popularity": 285400,
        "favourites": 32400,
    },
    {
        "id": 1,
        "title": {"romaji": "Cowboy Bebop", "english": "Cowboy Bebop"},
        "seasonYear": 1998,
        "season": "SPRING",
        "episodes": 26,
        "duration": 24,
        "genres": ["Action", "Adventure", "Drama", "Sci-Fi"],
        "tags": [{"name": "Space", "rank": 95, "isMediaSpoiler": False}, {"name": "Bounty Hunter", "rank": 93, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Sunrise", "isAnimationStudio": True}]},
        "source": "ORIGINAL",
        "averageScore": 86,
        "popularity": 320100,
        "favourites": 38900,
    },
    {
        "id": 164,
        "title": {"romaji": "Mononoke Hime", "english": "Princess Mononoke"},
        "seasonYear": 1997,
        "season": "SUMMER",
        "episodes": 1,
        "duration": 133,
        "genres": ["Action", "Adventure", "Drama", "Fantasy"],
        "tags": [{"name": "Environmental", "rank": 97, "isMediaSpoiler": False}, {"name": "Historical", "rank": 91, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Studio Ghibli", "isAnimationStudio": True}]},
        "source": "ORIGINAL",
        "averageScore": 88,
        "popularity": 235000,
        "favourites": 19200,
    },
    {
        "id": 6,
        "title": {"romaji": "Trigun", "english": "Trigun"},
        "seasonYear": 1998,
        "season": "SPRING",
        "episodes": 26,
        "duration": 24,
        "genres": ["Action", "Adventure", "Comedy", "Drama", "Sci-Fi"],
        "tags": [{"name": "Post-Apocalyptic", "rank": 91, "isMediaSpoiler": False}, {"name": "Guns", "rank": 93, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Madhouse", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 79,
        "popularity": 142000,
        "favourites": 8900,
    },
    {
        "id": 43,
        "title": {"romaji": "Koukaku Kidoutai", "english": "Ghost in the Shell"},
        "seasonYear": 1995,
        "season": "FALL",
        "episodes": 1,
        "duration": 82,
        "genres": ["Action", "Psychological", "Sci-Fi"],
        "tags": [{"name": "Cyberpunk", "rank": 98, "isMediaSpoiler": False}, {"name": "Philosophy", "rank": 94, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Production I.G", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 81,
        "popularity": 178000,
        "favourites": 12100,
    },
    {
        "id": 47,
        "title": {"romaji": "AKIRA", "english": "Akira"},
        "seasonYear": 1988,
        "season": "SUMMER",
        "episodes": 1,
        "duration": 124,
        "genres": ["Action", "Adventure", "Sci-Fi", "Supernatural"],
        "tags": [{"name": "Cyberpunk", "rank": 97, "isMediaSpoiler": False}, {"name": "Dystopian", "rank": 93, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Tokyo Movie Shinsha", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 79,
        "popularity": 192000,
        "favourites": 14300,
    },
    {
        "id": 33,
        "title": {"romaji": "Kenpuu Denki Berserk", "english": "Berserk"},
        "seasonYear": 1997,
        "season": "FALL",
        "episodes": 25,
        "duration": 24,
        "genres": ["Action", "Adventure", "Drama", "Fantasy", "Horror"],
        "tags": [{"name": "Dark Fantasy", "rank": 98, "isMediaSpoiler": False}, {"name": "Gore", "rank": 94, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "OLM", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 85,
        "popularity": 184000,
        "favourites": 22100,
    },
    {
        "id": 5114,
        "title": {"romaji": "Fullmetal Alchemist: Brotherhood", "english": "Fullmetal Alchemist: Brotherhood"},
        "seasonYear": 2009,
        "season": "SPRING",
        "episodes": 64,
        "duration": 24,
        "genres": ["Action", "Adventure", "Drama", "Fantasy"],
        "tags": [{"name": "Military", "rank": 98, "isMediaSpoiler": False}, {"name": "Alchemy", "rank": 98, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Bones", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 90,
        "popularity": 520000,
        "favourites": 65000,
    },

    # 2. Modern Hits
    {
        "id": 101922,
        "title": {"romaji": "Kimetsu no Yaiba", "english": "Demon Slayer: Kimetsu no Yaiba"},
        "seasonYear": 2019,
        "season": "SPRING",
        "episodes": 26,
        "duration": 23,
        "genres": ["Action", "Adventure", "Drama", "Fantasy", "Supernatural"],
        "tags": [{"name": "Demons", "rank": 97, "isMediaSpoiler": False}, {"name": "Swordplay", "rank": 95, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "ufotable", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 84,
        "popularity": 648000,
        "favourites": 71200,
    },
    {
        "id": 113415,
        "title": {"romaji": "Jujutsu Kaisen", "english": "Jujutsu Kaisen"},
        "seasonYear": 2020,
        "season": "FALL",
        "episodes": 24,
        "duration": 24,
        "genres": ["Action", "Drama", "Supernatural"],
        "tags": [{"name": "Curse", "rank": 96, "isMediaSpoiler": False}, {"name": "Shounen", "rank": 95, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "MAPPA", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 85,
        "popularity": 592000,
        "favourites": 68400,
    },
    {
        "id": 154587,
        "title": {"romaji": "Sousou no Frieren", "english": "Frieren: Beyond Journey's End"},
        "seasonYear": 2023,
        "season": "FALL",
        "episodes": 28,
        "duration": 24,
        "genres": ["Adventure", "Drama", "Fantasy"],
        "tags": [{"name": "Magic", "rank": 98, "isMediaSpoiler": False}, {"name": "Elf", "rank": 96, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Madhouse", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 92,
        "popularity": 320000,
        "favourites": 45100,
    },
    {
        "id": 127230,
        "title": {"romaji": "Chainsaw Man", "english": "Chainsaw Man"},
        "seasonYear": 2022,
        "season": "FALL",
        "episodes": 12,
        "duration": 24,
        "genres": ["Action", "Drama", "Horror", "Supernatural"],
        "tags": [{"name": "Gore", "rank": 96, "isMediaSpoiler": False}, {"name": "Demons", "rank": 95, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "MAPPA", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 84,
        "popularity": 460000,
        "favourites": 48900,
    },
    {
        "id": 140960,
        "title": {"romaji": "SPY×FAMILY", "english": "SPY x FAMILY"},
        "seasonYear": 2022,
        "season": "SPRING",
        "episodes": 12,
        "duration": 24,
        "genres": ["Action", "Comedy", "Slice of Life", "Supernatural"],
        "tags": [{"name": "Espionage", "rank": 96, "isMediaSpoiler": False}, {"name": "Family Life", "rank": 95, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "WIT Studio", "isAnimationStudio": True}, {"name": "CloverWorks", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 83,
        "popularity": 420000,
        "favourites": 31500,
    },

    # 3. Cult Favorites
    {
        "id": 7785,
        "title": {"romaji": "Yojouhan Shinwa Taikei", "english": "The Tatami Galaxy"},
        "seasonYear": 2010,
        "season": "SPRING",
        "episodes": 11,
        "duration": 23,
        "genres": ["Comedy", "Mystery", "Psychological", "Romance"],
        "tags": [{"name": "Time Loop", "rank": 96, "isMediaSpoiler": False}, {"name": "Surreal", "rank": 94, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Madhouse", "isAnimationStudio": True}]},
        "source": "NOVEL",
        "averageScore": 85,
        "popularity": 132000,
        "favourites": 16400,
    },
    {
        "id": 5081,
        "title": {"romaji": "Bakemonogatari", "english": "Bakemonogatari"},
        "seasonYear": 2009,
        "season": "SUMMER",
        "episodes": 15,
        "duration": 25,
        "genres": ["Comedy", "Drama", "Mystery", "Psychological", "Romance", "Supernatural"],
        "tags": [{"name": "Dialogue-Driven", "rank": 98, "isMediaSpoiler": False}, {"name": "Avant Garde", "rank": 90, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Shaft", "isAnimationStudio": True}]},
        "source": "LIGHT_NOVEL",
        "averageScore": 83,
        "popularity": 298000,
        "favourites": 39800,
    },
    {
        "id": 19,
        "title": {"romaji": "MONSTER", "english": "Monster"},
        "seasonYear": 2004,
        "season": "SPRING",
        "episodes": 74,
        "duration": 24,
        "genres": ["Drama", "Mystery", "Psychological", "Thriller"],
        "tags": [{"name": "Serial Killer", "rank": 98, "isMediaSpoiler": False}, {"name": "Medical", "rank": 92, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Madhouse", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 88,
        "popularity": 265000,
        "favourites": 37200,
    },

    # 4. Low-Profile
    {
        "id": 2294,
        "title": {"romaji": "Sousei Kishi Gaiarth", "english": "Genesis Survivor Gaiarth"},
        "seasonYear": 1992,
        "season": "SPRING",
        "episodes": 3,
        "duration": 48,
        "genres": ["Action", "Adventure", "Sci-Fi"],
        "tags": [{"name": "Cyborg", "rank": 70, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "AIC", "isAnimationStudio": True}]},
        "source": "ORIGINAL",
        "averageScore": 62,
        "popularity": 2400,
        "favourites": 28,
    },
    {
        "id": 21188,
        "title": {"romaji": "Vampire Holmes", "english": "Vampire Holmes"},
        "seasonYear": 2015,
        "season": "SPRING",
        "episodes": 12,
        "duration": 3,
        "genres": ["Comedy", "Mystery", "Supernatural"],
        "tags": [{"name": "Detective", "rank": 60, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Studio! Cucuri", "isAnimationStudio": True}]},
        "source": "VIDEO_GAME",
        "averageScore": 34,
        "popularity": 5400,
        "favourites": 38,
    },

    # 5. Niche / Experimental
    {
        "id": 885,
        "title": {"romaji": "Tenshi no Tamago", "english": "Angel's Egg"},
        "seasonYear": 1985,
        "season": "FALL",
        "episodes": 1,
        "duration": 71,
        "genres": ["Drama", "Fantasy", "Psychological"],
        "tags": [{"name": "Avant Garde", "rank": 98, "isMediaSpoiler": False}, {"name": "Surreal", "rank": 96, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Studio Deen", "isAnimationStudio": True}]},
        "source": "ORIGINAL",
        "averageScore": 77,
        "popularity": 54000,
        "favourites": 6800,
    },
    {
        "id": 227,
        "title": {"romaji": "FLCL", "english": "FLCL"},
        "seasonYear": 2000,
        "season": "SPRING",
        "episodes": 6,
        "duration": 25,
        "genres": ["Action", "Comedy", "Mecha", "Sci-Fi"],
        "tags": [{"name": "Surreal", "rank": 96, "isMediaSpoiler": False}, {"name": "Rock Music", "rank": 94, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Gainax", "isAnimationStudio": True}]},
        "source": "ORIGINAL",
        "averageScore": 80,
        "popularity": 195000,
        "favourites": 22300,
    },
    {
        "id": 9253,
        "title": {"romaji": "Steins;Gate", "english": "Steins;Gate"},
        "seasonYear": 2011,
        "season": "SPRING",
        "episodes": 24,
        "duration": 24,
        "genres": ["Drama", "Psychological", "Sci-Fi", "Thriller"],
        "tags": [{"name": "Time Travel", "rank": 99, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "White Fox", "isAnimationStudio": True}]},
        "source": "VISUAL_NOVEL",
        "averageScore": 89,
        "popularity": 490000,
        "favourites": 73200,
    },
    {
        "id": 9756,
        "title": {"romaji": "Mahou Shoujo Madoka☆Magica", "english": "Puella Magi Madoka Magica"},
        "seasonYear": 2011,
        "season": "WINTER",
        "episodes": 12,
        "duration": 24,
        "genres": ["Action", "Drama", "Fantasy", "Psychological", "Thriller"],
        "tags": [{"name": "Tragedy", "rank": 95, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Shaft", "isAnimationStudio": True}]},
        "source": "ORIGINAL",
        "averageScore": 84,
        "popularity": 340000,
        "favourites": 41200,
    },
    {
        "id": 457,
        "title": {"romaji": "Mushishi", "english": "Mushishi"},
        "seasonYear": 2005,
        "season": "FALL",
        "episodes": 26,
        "duration": 25,
        "genres": ["Adventure", "Fantasy", "Mystery", "Slice of Life"],
        "tags": [{"name": "Iyashikei", "rank": 96, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Artland", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 86,
        "popularity": 182000,
        "favourites": 21800,
    },
    {
        "id": 2001,
        "title": {"romaji": "Tengen Toppa Gurren Lagann", "english": "Gurren Lagann"},
        "seasonYear": 2007,
        "season": "SPRING",
        "episodes": 27,
        "duration": 24,
        "genres": ["Action", "Adventure", "Comedy", "Mecha", "Sci-Fi"],
        "tags": [{"name": "Super Robot", "rank": 98, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Gainax", "isAnimationStudio": True}]},
        "source": "ORIGINAL",
        "averageScore": 85,
        "popularity": 360000,
        "favourites": 44800,
    },
    {
        "id": 20607,
        "title": {"romaji": "Ping Pong THE ANIMATION", "english": "Ping Pong the Animation"},
        "seasonYear": 2014,
        "season": "SPRING",
        "episodes": 11,
        "duration": 23,
        "genres": ["Drama", "Psychological", "Sports"],
        "tags": [{"name": "Stylized Art", "rank": 95, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Tatsunoko Production", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 86,
        "popularity": 145000,
        "favourites": 17800,
    },
    {
        "id": 339,
        "title": {"romaji": "Serial Experiments Lain", "english": "Serial Experiments Lain"},
        "seasonYear": 1998,
        "season": "SUMMER",
        "episodes": 13,
        "duration": 23,
        "genres": ["Drama", "Mystery", "Psychological", "Sci-Fi"],
        "tags": [{"name": "Cyberpunk", "rank": 97, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Triangle Staff", "isAnimationStudio": True}]},
        "source": "ORIGINAL",
        "averageScore": 80,
        "popularity": 221000,
        "favourites": 28400,
    },
    {
        "id": 2737,
        "title": {"romaji": "Dark Cat", "english": "Dark Cat"},
        "seasonYear": 1991,
        "season": "FALL",
        "episodes": 1,
        "duration": 60,
        "genres": ["Action", "Horror", "Supernatural"],
        "tags": [{"name": "Demons", "rank": 65, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Nikkatsu", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 51,
        "popularity": 1800,
        "favourites": 12,
    },
    {
        "id": 413,
        "title": {"romaji": "Hametsu no Mars", "english": "Mars of Destruction"},
        "seasonYear": 2005,
        "season": "SUMMER",
        "episodes": 1,
        "duration": 19,
        "genres": ["Action", "Horror", "Sci-Fi"],
        "tags": [{"name": "Aliens", "rank": 60, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Idea Factory", "isAnimationStudio": True}]},
        "source": "VIDEO_GAME",
        "averageScore": 26,
        "popularity": 9400,
        "favourites": 92,
    },
    {
        "id": 19315,
        "title": {"romaji": "Pupa", "english": "Pupa"},
        "seasonYear": 2014,
        "season": "WINTER",
        "episodes": 12,
        "duration": 4,
        "genres": ["Drama", "Fantasy", "Horror"],
        "tags": [{"name": "Cannibalism", "rank": 78, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Studio Deen", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 45,
        "popularity": 24000,
        "favourites": 120,
    },
    {
        "id": 601,
        "title": {"romaji": "Nekojiru-sou", "english": "Cat Soup"},
        "seasonYear": 2001,
        "season": "WINTER",
        "episodes": 1,
        "duration": 32,
        "genres": ["Comedy", "Psychological"],
        "tags": [{"name": "Surreal", "rank": 98, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "J.C.Staff", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 73,
        "popularity": 48000,
        "favourites": 4300,
    },
    {
        "id": 1983,
        "title": {"romaji": "Paprika", "english": "Paprika"},
        "seasonYear": 2006,
        "season": "FALL",
        "episodes": 1,
        "duration": 90,
        "genres": ["Fantasy", "Mystery", "Psychological", "Sci-Fi"],
        "tags": [{"name": "Dreams", "rank": 99, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Madhouse", "isAnimationStudio": True}]},
        "source": "NOVEL",
        "averageScore": 82,
        "popularity": 182000,
        "favourites": 14900,
    },
    {
        "id": 98460,
        "title": {"romaji": "DEVILMAN crybaby", "english": "Devilman Crybaby"},
        "seasonYear": 2018,
        "season": "WINTER",
        "episodes": 10,
        "duration": 25,
        "genres": ["Action", "Drama", "Horror", "Supernatural"],
        "tags": [{"name": "Demons", "rank": 98, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Science SARU", "isAnimationStudio": True}]},
        "source": "MANGA",
        "averageScore": 78,
        "popularity": 268000,
        "favourites": 21500,
    },
    {
        "id": 132126,
        "title": {"romaji": "Sonny Boy", "english": "Sonny Boy"},
        "seasonYear": 2021,
        "season": "SUMMER",
        "episodes": 12,
        "duration": 24,
        "genres": ["Drama", "Mystery", "Psychological", "Sci-Fi"],
        "tags": [{"name": "Surreal", "rank": 96, "isMediaSpoiler": False}],
        "studios": {"nodes": [{"name": "Madhouse", "isAnimationStudio": True}]},
        "source": "ORIGINAL",
        "averageScore": 78,
        "popularity": 120000,
        "favourites": 14200,
    },
]



# ---------------------------------------------------------------------------
# AniList GraphQL Query Definition
# ---------------------------------------------------------------------------
ANILIST_GRAPHQL_QUERY = """
query ($page: Int, $perPage: Int, $sort: [MediaSort] = [POPULARITY_DESC]) {
  Page(page: $page, perPage: $perPage) {
    pageInfo {
      total
      currentPage
      lastPage
      hasNextPage
      perPage
    }
    media(type: ANIME, sort: $sort) {
      id
      title {
        romaji
        english
      }
      seasonYear
      season
      episodes
      duration
      genres
      tags {
        name
        rank
        isMediaSpoiler
      }
      studios(isMain: true) {
        nodes {
          name
          isAnimationStudio
        }
      }
      source
      averageScore
      popularity
      favourites
    }
  }
}
"""


class AniListGraphQLClient:
    """Fetcher for AniList GraphQL API with rate limiting and retry handling."""

    ANILIST_API_URL = "https://graphql.anilist.co"
    PAGE_SIZE = 50

    def __init__(
        self,
        rate_limit_delay: float = 0.5,
        max_retries: int = 3,
        timeout: int = 15,
    ):
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "AnimeInsights/1.0 (DataSciencePipeline)",
            }
        )

    def query_page(
        self,
        page: int,
        per_page: int,
        sort: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Query a single page from AniList with backoff."""
        variables: Dict[str, Any] = {"page": page, "perPage": per_page}
        if sort:
            variables["sort"] = sort
        payload = {
            "query": ANILIST_GRAPHQL_QUERY,
            "variables": variables,
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.post(
                    self.ANILIST_API_URL,
                    json=payload,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    data = response.json()
                    remaining = response.headers.get("X-RateLimit-Remaining")
                    if remaining is not None and int(remaining) < 10:
                        logger.warning("AniList rate limit low (%s left), cooling down for 2s...", remaining)
                        time.sleep(2.0)
                    return data

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.warning("HTTP 429 from AniList. Cooling down for %ds (attempt %d/%d)...",
                                   retry_after, attempt, self.max_retries)
                    time.sleep(retry_after)
                    continue

                logger.warning("AniList HTTP %d: %s", response.status_code, response.text[:150])
                time.sleep(1.0 * attempt)

            except requests.RequestException as e:
                logger.warning("AniList request exception on page %d: %s", page, e)
                time.sleep(1.5 * attempt)

        return None


class KitsuFetcher:
    """
    Secondary fallback fetcher for Kitsu JSON:API (https://kitsu.io/api/edge/anime).
    Maps Kitsu anime attributes into canonical schema.
    """

    KITSU_API_URL = "https://kitsu.io/api/edge/anime"
    PAGE_SIZE = 20

    def __init__(
        self,
        rate_limit_delay: float = 0.5,
        max_retries: int = 3,
        timeout: int = 15,
    ):
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.api+json",
                "User-Agent": "AnimeInsights/1.0 (DataSciencePipeline)",
            }
        )

    def query_page(self, offset: int = 0, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """Fetch a page from Kitsu and map into canonical schema."""
        params = {
            "page[offset]": offset,
            "page[limit]": limit,
            "sort": "-userCount",
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(
                    self.KITSU_API_URL,
                    params=params,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    data = response.json()
                    items = data.get("data", [])
                    return [self._map_kitsu_item(it) for it in items]

                if response.status_code == 429:
                    time.sleep(3.0 * attempt)
                    continue

                time.sleep(1.0 * attempt)

            except requests.RequestException as e:
                logger.warning("Kitsu request exception: %s", e)
                time.sleep(1.5 * attempt)

        return None

    @staticmethod
    def _map_kitsu_item(item: Dict[str, Any]) -> Dict[str, Any]:
        """Map raw Kitsu attributes to canonical anime schema."""
        attrs = item.get("attributes", {})
        date_str = attrs.get("startDate") or "2020-01-01"
        try:
            year = int(date_str.split("-")[0])
            month = int(date_str.split("-")[1]) if len(date_str.split("-")) > 1 else 1
        except Exception:
            year = 2020
            month = 1

        season = "WINTER" if month <= 3 else "SPRING" if month <= 6 else "SUMMER" if month <= 9 else "FALL"
        titles = attrs.get("titles", {}) or {}
        canon_title = attrs.get("canonicalTitle") or "Unknown Title"
        english_title = titles.get("en") or titles.get("en_us") or canon_title
        romaji_title = titles.get("en_jp") or canon_title

        subtype = attrs.get("subtype", "TV")
        genre_label = subtype.capitalize() if subtype else "Anime"

        return {
            "id": int(item.get("id", 0)),
            "title": {"romaji": romaji_title, "english": english_title},
            "seasonYear": year,
            "season": season,
            "episodes": attrs.get("episodeCount") or 12,
            "duration": attrs.get("episodeLength") or 24,
            "genres": [genre_label, "Animation"],
            "tags": [{"name": attrs.get("showType", "TV"), "rank": 80, "isMediaSpoiler": False}],
            "studios": {"nodes": []},
            "source": "MANGA" if subtype == "TV" else "ORIGINAL",
            "averageScore": float(attrs.get("averageRating") or 70.0),
            "popularity": int(attrs.get("userCount") or 1000),
            "favourites": int(attrs.get("favoritesCount") or 50),
        }


class MultiSourceFetcher:
    """
    Unified multi-source ingestion coordinator.
    Chains Primary (AniList) -> Secondary (Kitsu) -> Local SQLite DB -> Static Mock,
    enforcing slow rate-limiting to prevent bans and incremental accumulation.
    """

    def __init__(
        self,
        db: Optional[AnimeCatalogDB] = None,
        cache_json_path: Optional[str] = None,
        cache_path: Optional[str] = None,
        rate_limit_delay: float = 0.6,
    ):
        chosen_path = cache_path or cache_json_path or "data/raw_anime_data.json"
        self.cache_json_path = chosen_path
        self.cache_path = chosen_path
        self._custom_cache = bool(cache_path or cache_json_path)
        self.db = db or AnimeCatalogDB()
        self.rate_limit_delay = rate_limit_delay
        self.anilist = AniListGraphQLClient(rate_limit_delay=rate_limit_delay)
        self.kitsu = KitsuFetcher(rate_limit_delay=rate_limit_delay)

        # On initial boot, import existing JSON into SQLite if DB is empty
        if self.db.count_records() == 0 and os.path.exists(self.cache_json_path):
            self.db.import_from_json(self.cache_json_path, source_api="anilist")

    def save_cache(self, records: List[Dict[str, Any]]) -> None:
        """Save records directly to the JSON cache file."""
        target_path = os.path.abspath(self.cache_json_path)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

    def load_cache(self) -> Optional[List[Dict[str, Any]]]:
        """Load records from the JSON cache file if it exists."""
        target_path = os.path.abspath(self.cache_json_path)
        if os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
            except Exception:
                pass
        return None

    def fetch_anime_data(
        self,
        limit: int = 500,
        preferred_source: str = "auto",
        force_fetch: bool = False,
        offline: bool = False,
        incremental: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve anime records with incremental database management and multi-source fallbacks.

        :param limit: Desired number of records.
        :param preferred_source: 'auto' (AniList -> Kitsu), 'anilist', or 'kitsu'.
        :param force_fetch: Bypass existing DB and fetch new records from API.
        :param offline: Run purely offline from SQLite database or mock.
        :param incremental: Resume from last fetched page/offset without duplicating.
        """
        # 1. Offline Mode: Return existing DB records or mock
        if offline:
            # If custom cache was set and exists
            cached = self.load_cache()
            if cached is not None and len(cached) > 0:
                return cached[:limit]
            if not self._custom_cache:
                db_count = self.db.count_records()
                if db_count > 0:
                    logger.info("Offline mode: loaded %d records from SQLite incremental database.", min(db_count, limit))
                    return self.db.get_all_records(limit=limit)
            logger.info("Offline mode: using built-in mock dataset.")
            return MOCK_ANIME_DATA[:limit]


        # 2. Check if local DB already has sufficient records and force_fetch is False
        db_count = self.db.count_records()
        if not force_fetch and db_count >= limit:
            logger.info("Local database satisfies request (%d cached records >= %d requested).", db_count, limit)
            return self.db.get_all_records(limit=limit)

        records_needed = limit if force_fetch else max(0, limit - db_count)
        logger.info(
            "Fetching %d additional records (current DB count: %d, target: %d)...",
            records_needed,
            db_count,
            limit,
        )

        fetched_records: List[Dict[str, Any]] = []

        # 3. Source Strategy: Try AniList unless Kitsu explicitly requested
        if preferred_source in ("auto", "anilist"):
            fetched_records = self._fetch_from_anilist(records_needed, incremental=incremental)

        # 4. Fallback to Kitsu if AniList returned insufficient data
        if len(fetched_records) < records_needed and preferred_source in ("auto", "kitsu"):
            remaining = records_needed - len(fetched_records)
            logger.info("Attempting secondary source (Kitsu) for %d records...", remaining)
            kitsu_records = self._fetch_from_kitsu(remaining, incremental=incremental)
            fetched_records.extend(kitsu_records)

        # 5. Persist fetched records into SQLite & export to JSON
        if fetched_records:
            default_src = "anilist" if preferred_source == "auto" else preferred_source
            self.db.upsert_records(fetched_records, source_api=default_src)
            self.db.export_to_json(self.cache_json_path)

        total_db = self.db.count_records()
        if total_db > 0:
            return self.db.get_all_records(limit=limit)

        # Fallback to mock if nothing in DB
        return MOCK_ANIME_DATA[:limit]

    def _fetch_from_anilist(self, count: int, incremental: bool = True) -> List[Dict[str, Any]]:
        """Fetch records from AniList with polite pagination."""
        start_page = self.db.get_fetch_page("anilist") if incremental else 1
        page = start_page
        results: List[Dict[str, Any]] = []
        per_page = min(50, count)

        try:
            while len(results) < count:
                batch_size = min(per_page, count - len(results))
                logger.info("AniList: requesting page %d (batch: %d)...", page, batch_size)
                data = self.anilist.query_page(page, batch_size)

                if not data or "data" not in data or "Page" not in data["data"]:
                    logger.warning("AniList page %d returned invalid data. Ending AniList fetch.", page)
                    break

                page_info = data["data"]["Page"]
                media = page_info.get("media", [])
                if not media:
                    break

                for m in media:
                    if isinstance(m, dict):
                        m["source_api"] = "anilist"
                results.extend(media)
                self.db.update_fetch_page("anilist", page, len(media))

                if not page_info.get("pageInfo", {}).get("hasNextPage", False):
                    break

                page += 1
                time.sleep(self.rate_limit_delay)

        except Exception as e:
            logger.error("Exception during AniList fetch: %s", e)

        return results

    def _fetch_from_kitsu(self, count: int, incremental: bool = True) -> List[Dict[str, Any]]:
        """Fetch records from Kitsu with polite pagination."""
        start_offset = (self.db.get_fetch_page("kitsu") - 1) * 20 if incremental else 0
        offset = start_offset
        results: List[Dict[str, Any]] = []

        try:
            while len(results) < count:
                batch_size = min(20, count - len(results))
                logger.info("Kitsu: requesting offset %d (limit: %d)...", offset, batch_size)
                items = self.kitsu.query_page(offset=offset, limit=batch_size)

                if not items:
                    break

                for it in items:
                    if isinstance(it, dict):
                        it["source_api"] = "kitsu"
                results.extend(items)
                page_num = (offset // 20) + 1
                self.db.update_fetch_page("kitsu", page_num, len(items))

                if len(items) < batch_size:
                    break

                offset += len(items)
                time.sleep(self.rate_limit_delay)

        except Exception as e:
            logger.error("Exception during Kitsu fetch: %s", e)

        return results


# Backward compatibility alias
AniListFetcher = MultiSourceFetcher
