"""
Origin Classifier Module for Anime National Cohorting.

Implements a deterministic 5-level cascade to classify anime titles into:
1. Binary Cohort: 'jp' (Japanese domestic) vs 'non-jp' (International / Overseas)
2. Granular Sub-Origin: 'JP', 'CN' (Chinese Donghua), 'KR' (Korean Aeni),
   'WESTERN' (US/Europe/Global), and 'OTHER'.

Follows a multi-signal priority rule with standard Japanese catalog default.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("origin_classifier")


@dataclass(frozen=True)
class OriginClassificationResult:
    """Immutable result of origin classification cascade."""
    origin_cohort: str      # 'jp' or 'non-jp'
    sub_origin: str         # 'JP', 'CN', 'KR', 'WESTERN', 'OTHER'
    is_jp: int              # 1 for JP, 0 for Non-JP
    detection_level: int    # 1 (metadata) to 5 (default fallback)
    rule_name: str          # Descriptive identifier of triggered rule
    confidence: float       # Confidence score [0.50, 1.00]


class AnimeOriginClassifier:
    """
    Multi-tiered cascade classifier for anime national origin.
    Cascade order:
    1. Ground-Truth Country Metadata (AniList countryOfOrigin)
    2. Tag & Keyword Heuristics ('chinese animation', 'donghua', 'korean animation', 'aeni')
    3. Animation Studio Gazetteers (Haoliners, Tencent, Studio Mir, Rooster Teeth vs Toei, MAPPA)
    4. Unicode Script Detection on native titles & synonyms (Kana -> JP, Hangul -> KR, Bopomofo -> CN)
    5. Baseline Japanese Catalog Default
    """

    # Level 1: Country Code Crosswalk
    COUNTRY_MAP: Dict[str, Tuple[str, str, int]] = {
        "JP": ("jp", "JP", 1),
        "CN": ("non-jp", "CN", 0),
        "TW": ("non-jp", "CN", 0),
        "HK": ("non-jp", "CN", 0),
        "KR": ("non-jp", "KR", 0),
        "KP": ("non-jp", "KR", 0),
        "US": ("non-jp", "WESTERN", 0),
        "GB": ("non-jp", "WESTERN", 0),
        "FR": ("non-jp", "WESTERN", 0),
        "CA": ("non-jp", "WESTERN", 0),
        "DE": ("non-jp", "WESTERN", 0),
        "AU": ("non-jp", "WESTERN", 0),
        "IT": ("non-jp", "WESTERN", 0),
        "ES": ("non-jp", "WESTERN", 0),
        "RU": ("non-jp", "WESTERN", 0),
    }

    # Level 2: Tag & Keyword Patterns
    TAG_PATTERNS: List[Tuple[re.Pattern, str, str, int, str]] = [
        (
            re.compile(
                r"\b(chinese animation|donghua|chinese production|ancient china|xianxia|wuxia|chinese mythology|manhua|bilibili original|sino-japanese co-production)\b",
                re.IGNORECASE,
            ),
            "non-jp",
            "CN",
            0,
            "tag_chinese_donghua",
        ),
        (
            re.compile(
                r"\b(korean animation|south korean production|aeni|manhwa|webtoon|korea)\b",
                re.IGNORECASE,
            ),
            "non-jp",
            "KR",
            0,
            "tag_korean_aeni",
        ),
        (
            re.compile(
                r"\b(western animation|american animation|french animation|western animated cartoon|original in english|american derived|western comics|rooster teeth|disney\+ original)\b",
                re.IGNORECASE,
            ),
            "non-jp",
            "WESTERN",
            0,
            "tag_western_anim",
        ),
        (
            re.compile(
                r"\b(japanese production|japanese mythology|feudal japan|japan animator's exhibition|japanese anime classic collection)\b",
                re.IGNORECASE,
            ),
            "jp",
            "JP",
            1,
            "tag_japanese_anime",
        ),
    ]

    # Level 3: Known Studio Gazetteers (normalized lowercase)
    STUDIO_REGISTRY: Dict[str, Tuple[str, str, int]] = {
        # Chinese Studios & Producers
        "tencent penguin pictures": ("non-jp", "CN", 0),
        "tencent animation": ("non-jp", "CN", 0),
        "bilibili": ("non-jp", "CN", 0),
        "haoliners animation league": ("non-jp", "CN", 0),
        "sparkly key animation": ("non-jp", "CN", 0),
        "foch film": ("non-jp", "CN", 0),
        "studio lan": ("non-jp", "CN", 0),
        "colored-pencil animation design": ("non-jp", "CN", 0),
        "g.c.may animation & film": ("non-jp", "CN", 0),
        "papergames": ("non-jp", "CN", 0),
        "b.cmay pictures": ("non-jp", "CN", 0),
        "nice boat animation": ("non-jp", "CN", 0),
        "beijing sharefun media": ("non-jp", "CN", 0),
        "wonder cat animation": ("non-jp", "CN", 0),
        "l²studio": ("non-jp", "CN", 0),
        "chongzhuo animation": ("non-jp", "CN", 0),
        "recolored animation": ("non-jp", "CN", 0),

        # Korean Studios
        "studio mir": ("non-jp", "KR", 0),
        "dr movie": ("non-jp", "KR", 0),
        "studio gale": ("non-jp", "KR", 0),
        "dong woo animation": ("non-jp", "KR", 0),
        "red dog culture house": ("non-jp", "KR", 0),
        "iconix entertainment": ("non-jp", "KR", 0),
        "studio animal": ("non-jp", "KR", 0),
        "studio ppuri": ("non-jp", "KR", 0),

        # Western Studios
        "rooster teeth": ("non-jp", "WESTERN", 0),
        "powerhouse animation studios": ("non-jp", "WESTERN", 0),
        "titmouse": ("non-jp", "WESTERN", 0),
        "frederator studios": ("non-jp", "WESTERN", 0),
        "fortiche production": ("non-jp", "WESTERN", 0),
        "nickelodeon animation studio": ("non-jp", "WESTERN", 0),

        # Japanese Studios (Prominent anchors)
        "toei animation": ("jp", "JP", 1),
        "sunrise": ("jp", "JP", 1),
        "bones": ("jp", "JP", 1),
        "madhouse": ("jp", "JP", 1),
        "mappa": ("jp", "JP", 1),
        "ufotable": ("jp", "JP", 1),
        "kyoto animation": ("jp", "JP", 1),
        "a-1 pictures": ("jp", "JP", 1),
        "cloverworks": ("jp", "JP", 1),
        "wit studio": ("jp", "JP", 1),
        "production i.g": ("jp", "JP", 1),
        "shaft": ("jp", "JP", 1),
        "trigger": ("jp", "JP", 1),
        "j.c.staff": ("jp", "JP", 1),
        "tms entertainment": ("jp", "JP", 1),
        "pierrot": ("jp", "JP", 1),
        "studio ghibli": ("jp", "JP", 1),
        "gainax": ("jp", "JP", 1),
        "science saru": ("jp", "JP", 1),
        "doga kobo": ("jp", "JP", 1),
        "silver link.": ("jp", "JP", 1),
    }

    # Level 4: Unicode Script Regex
    # Kana (Hiragana \u3040-\u309F, Katakana \u30A0-\u30FF) -> Exclusively Japanese
    RE_KANA = re.compile(r"[\u3040-\u309F\u30A0-\u30FF]")
    # Hangul (Syllables \uAC00-\uD7AF, Jamo \u1100-\u11FF, \u3130-\u318F) -> Exclusively Korean
    RE_HANGUL = re.compile(r"[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]")
    # Bopomofo (\u3100-\u312F) -> Traditional Chinese
    RE_BOPOMOFO = re.compile(r"[\u3100-\u312F]")

    def classify_record(self, record: Dict[str, Any]) -> OriginClassificationResult:
        """
        Classify a single anime record dictionary through the 5-tier cascade.

        :param record: Raw or preprocessed anime metadata dictionary.
        :return: OriginClassificationResult
        """
        if not isinstance(record, dict):
            return OriginClassificationResult("jp", "JP", 1, 5, "default_invalid_record", 0.50)

        # Level 1: AniList countryOfOrigin or country
        country_raw = record.get("countryOfOrigin") or record.get("country")
        if country_raw and isinstance(country_raw, str):
            code = country_raw.strip().upper()
            if code in self.COUNTRY_MAP:
                cohort, subtag, is_jp = self.COUNTRY_MAP[code]
                return OriginClassificationResult(cohort, subtag, is_jp, 1, f"country_of_origin_{code}", 1.00)
            is_jp = 1 if code == "JP" else 0
            cohort = "jp" if is_jp else "non-jp"
            subtag = "JP" if is_jp else "OTHER"
            return OriginClassificationResult(cohort, subtag, is_jp, 1, f"country_of_origin_{code}", 0.90)

        # Level 2: Tag keywords & Source Material
        source_mat = str(record.get("source") or record.get("source_material") or "").upper()
        if source_mat == "MANHUA":
            return OriginClassificationResult("non-jp", "CN", 0, 2, "source_manhua", 0.95)
        elif source_mat in ("MANHWA", "WEBTOON"):
            return OriginClassificationResult("non-jp", "KR", 0, 2, "source_manhwa", 0.95)
        elif source_mat == "COMIC":
            return OriginClassificationResult("non-jp", "WESTERN", 0, 2, "source_comic", 0.90)

        tag_text = self._extract_tag_text(record)
        if tag_text:
            for pattern, cohort, subtag, is_jp, rule_id in self.TAG_PATTERNS:
                if pattern.search(tag_text):
                    return OriginClassificationResult(cohort, subtag, is_jp, 2, rule_id, 0.85)

        # Level 3: Known Studio Provenance
        studios = self._extract_studio_names(record)
        for studio in studios:
            s_clean = studio.strip().lower()
            if s_clean in self.STUDIO_REGISTRY:
                cohort, subtag, is_jp = self.STUDIO_REGISTRY[s_clean]
                return OriginClassificationResult(cohort, subtag, is_jp, 3, f"studio_{s_clean}", 0.80)

        # Level 4: Unicode Script Detection on native titles & synonyms
        title_text = self._extract_title_text(record)
        if self.RE_HANGUL.search(title_text):
            return OriginClassificationResult("non-jp", "KR", 0, 4, "script_hangul", 0.75)
        if self.RE_KANA.search(title_text):
            return OriginClassificationResult("jp", "JP", 1, 4, "script_kana", 0.75)
        if self.RE_BOPOMOFO.search(title_text):
            return OriginClassificationResult("non-jp", "CN", 0, 4, "script_bopomofo", 0.75)

        # Level 5: Default Fallback to Japanese domestic baseline
        return OriginClassificationResult("jp", "JP", 1, 5, "default_fallback_jp", 0.50)

    @staticmethod
    def _extract_tag_text(record: Dict[str, Any]) -> str:
        """Extract concatenated tag names and genres."""
        parts: List[str] = []
        tags = record.get("tags")
        if isinstance(tags, list):
            for t in tags:
                if isinstance(t, dict):
                    name = t.get("name")
                    if name:
                        parts.append(str(name))
                elif isinstance(t, str):
                    parts.append(t)

        genres = record.get("genres")
        if isinstance(genres, list):
            for g in genres:
                if isinstance(g, str):
                    parts.append(g)

        return " ".join(parts).lower()

    @staticmethod
    def _extract_studio_names(record: Dict[str, Any]) -> List[str]:
        """Extract studio names from diverse representations."""
        studios_obj = record.get("studios")
        names: List[str] = []

        if isinstance(studios_obj, dict):
            nodes = studios_obj.get("nodes") or []
            if isinstance(nodes, list):
                for n in nodes:
                    if isinstance(n, dict) and "name" in n:
                        names.append(str(n["name"]))
                    elif isinstance(n, str):
                        names.append(n)
        elif isinstance(studios_obj, list):
            for s in studios_obj:
                if isinstance(s, dict) and "name" in s:
                    names.append(str(s["name"]))
                elif isinstance(s, str):
                    names.append(s)

        return names

    @staticmethod
    def _extract_title_text(record: Dict[str, Any]) -> str:
        """Extract all title representations (romaji, english, native, synonyms)."""
        parts: List[str] = []
        title_obj = record.get("title")

        if isinstance(title_obj, dict):
            for k in ("native", "romaji", "english"):
                val = title_obj.get(k)
                if val and isinstance(val, str):
                    parts.append(val)
        elif isinstance(title_obj, str):
            parts.append(title_obj)

        for col in ("title_romaji", "title_english"):
            col_val = record.get(col)
            if col_val and isinstance(col_val, str):
                parts.append(col_val)

        synonyms = record.get("synonyms")
        if isinstance(synonyms, list):
            for s in synonyms:
                if isinstance(s, str):
                    parts.append(s)

        return " ".join(parts)


# Module-level convenience singleton
_DEFAULT_CLASSIFIER = AnimeOriginClassifier()


def classify_anime_origin(record: Dict[str, Any]) -> OriginClassificationResult:
    """Convenience helper to classify a record using the default classifier instance."""
    return _DEFAULT_CLASSIFIER.classify_record(record)
