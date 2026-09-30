"""
Unit tests for the Anime Origin Classifier.
"""

import pytest
from src.origin_classifier import AnimeOriginClassifier, classify_anime_origin


def test_level1_country_code_metadata():
    """Verify Level 1 explicit country code detection."""
    classifier = AnimeOriginClassifier()

    # AniList country code CN
    res_cn = classifier.classify_record({"countryOfOrigin": "CN", "title": "Mo Dao Zu Shi"})
    assert res_cn.origin_cohort == "non-jp"
    assert res_cn.sub_origin == "CN"
    assert res_cn.is_jp == 0
    assert res_cn.detection_level == 1

    # AniList country code KR
    res_kr = classifier.classify_record({"countryOfOrigin": "KR", "title": "Lookism"})
    assert res_kr.origin_cohort == "non-jp"
    assert res_kr.sub_origin == "KR"
    assert res_kr.is_jp == 0

    # AniList country code JP
    res_jp = classifier.classify_record({"countryOfOrigin": "JP", "title": "Cowboy Bebop"})
    assert res_jp.origin_cohort == "jp"
    assert res_jp.sub_origin == "JP"
    assert res_jp.is_jp == 1

    # Western country code US
    res_us = classifier.classify_record({"countryOfOrigin": "US", "title": "Castlevania"})
    assert res_us.origin_cohort == "non-jp"
    assert res_us.sub_origin == "WESTERN"
    assert res_us.is_jp == 0


def test_level2_tags_and_source_material():
    """Verify Level 2 tag keyword and source material heuristic."""
    classifier = AnimeOriginClassifier()

    # Tag: Chinese animation / Donghua
    res_donghua = classifier.classify_record({
        "title": "Quanzhi Gaoshou",
        "tags": [{"name": "Chinese Animation"}, {"name": "Esports"}],
    })
    assert res_donghua.origin_cohort == "non-jp"
    assert res_donghua.sub_origin == "CN"
    assert res_donghua.detection_level == 2

    # Tag: Korean animation / Aeni
    res_aeni = classifier.classify_record({
        "title": "Aeni Test",
        "tags": ["Korean Animation", "Drama"],
    })
    assert res_aeni.origin_cohort == "non-jp"
    assert res_aeni.sub_origin == "KR"
    assert res_aeni.detection_level == 2

    # Source Material: MANHUA
    res_manhua = classifier.classify_record({
        "title": "Manhua Adaptation",
        "source": "MANHUA",
    })
    assert res_manhua.origin_cohort == "non-jp"
    assert res_manhua.sub_origin == "CN"

    # Source Material: MANHWA / WEBTOON
    res_manhwa = classifier.classify_record({
        "title": "Tower of God",
        "source": "MANHWA",
    })
    assert res_manhwa.origin_cohort == "non-jp"
    assert res_manhwa.sub_origin == "KR"


def test_level3_studio_provenance():
    """Verify Level 3 studio gazetteer matching."""
    classifier = AnimeOriginClassifier()

    # Chinese studio: Haoliners Animation League
    res_haoliners = classifier.classify_record({
        "title": "Ling Qi",
        "studios": {"nodes": [{"name": "Haoliners Animation League"}]},
    })
    assert res_haoliners.origin_cohort == "non-jp"
    assert res_haoliners.sub_origin == "CN"
    assert res_haoliners.detection_level == 3

    # Korean studio: Studio Mir
    res_mir = classifier.classify_record({
        "title": "Dota: Dragon's Blood",
        "studios": [{"name": "Studio Mir"}],
    })
    assert res_mir.origin_cohort == "non-jp"
    assert res_mir.sub_origin == "KR"
    assert res_mir.detection_level == 3

    # Japanese studio: MAPPA
    res_mappa = classifier.classify_record({
        "title": "Jujutsu Kaisen",
        "studios": {"nodes": [{"name": "MAPPA"}]},
    })
    assert res_mappa.origin_cohort == "jp"
    assert res_mappa.sub_origin == "JP"
    assert res_mappa.detection_level == 3


def test_level4_script_detection():
    """Verify Level 4 Unicode script detection on native titles and synonyms."""
    classifier = AnimeOriginClassifier()

    # Hangul in title -> KR
    res_hangul = classifier.classify_record({
        "title": {"native": "신의 탑", "romaji": "Sin-ui Tap"},
    })
    assert res_hangul.origin_cohort == "non-jp"
    assert res_hangul.sub_origin == "KR"
    assert res_hangul.detection_level == 4

    # Hiragana / Katakana in title -> JP
    res_kana = classifier.classify_record({
        "title": {"native": "鬼滅の刃", "romaji": "Kimetsu no Yaiba"},
    })
    assert res_kana.origin_cohort == "jp"
    assert res_kana.sub_origin == "JP"
    assert res_kana.detection_level == 4


def test_level5_default_japanese_baseline():
    """Verify Level 5 fallback to JP domestic catalog baseline."""
    classifier = AnimeOriginClassifier()

    # Completely untagged / ambiguous title
    res_default = classifier.classify_record({
        "title": "Classic Legend",
        "seasonYear": 1998,
        "episodes": 26,
    })
    assert res_default.origin_cohort == "jp"
    assert res_default.sub_origin == "JP"
    assert res_default.is_jp == 1
    assert res_default.detection_level == 5

    # Invalid input handling
    res_invalid = classifier.classify_record(None)  # type: ignore
    assert res_invalid.origin_cohort == "jp"
    assert res_invalid.is_jp == 1
