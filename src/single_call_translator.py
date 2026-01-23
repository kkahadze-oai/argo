#!/usr/bin/env python3
"""
Single-call translation system using dictionary lookups and one LLM API call.
Adapted from explore_rag_dict.ipynb notebook.
"""
import re
import string
from pathlib import Path
from typing import Callable, Optional
try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None

from src.logger import (
    setup_logger, 
    log_prompt, 
    log_llm_response, 
    log_instant_lookup,
    log_stage_timing
)
import time

# Setup logger for translator module
logger = setup_logger('translator')


# Language labels for prompts
LANG_LABEL = {
    "mingrelian": "Mingrelian",
    "english": "English",
    "georgian": "Georgian",
}


def _get_data_path(filename: str) -> str:
    """Get the path to a data file, checking multiple possible locations."""
    # Try fastapi_app/data first (for API usage)
    fastapi_data = Path(__file__).parent.parent / 'fastapi_app' / 'data' / filename
    if fastapi_data.exists():
        return str(fastapi_data)
    
    # Try parent data directory
    parent_data = Path(__file__).parent.parent / 'data' / filename
    if parent_data.exists():
        return str(parent_data)
    
    # Try notebooks directory (for development)
    notebooks_data = Path(__file__).parent.parent / 'notebooks' / filename
    if notebooks_data.exists():
        return str(notebooks_data)
    
    # Try notebooks/dicts directory
    notebooks_dicts = Path(__file__).parent.parent / 'notebooks' / 'dicts' / filename
    if notebooks_dicts.exists():
        return str(notebooks_dicts)
    
    # Default to fastapi_app/data
    return str(fastapi_data)


def _is_standalone_match(text: str, word: str) -> bool:
    """
    Check if word appears as a standalone word in text (not as part of another word).
    Uses regex word boundaries to match complete words only.
    
    Args:
        text: Text to search in
        word: Word to search for
        
    Returns:
        bool: True if word appears standalone, False otherwise
    """
    # Escape special regex characters in the word
    escaped_word = re.escape(word)
    # Use word boundaries \b to match complete words only
    pattern = r'\b' + escaped_word + r'\b'
    return bool(re.search(pattern, text, re.IGNORECASE))


# English
def grep_search_pairs(word: str) -> tuple[str, bool]:
    """
    Search sentence_pairs.tsv for English translations, prioritizing standalone word matches.
    Returns: (result_string, has_standalone_matches)
    """
    file_path = _get_data_path("sentence_pairs.tsv")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return "", False
    
    # First pass: look for standalone word matches
    standalone_output = "========\n"
    substring_output = "========\n"
    
    for line in lines:
        parts = line.split("\t")
        if len(parts) >= 2:
            mingrelian, english = parts[0], parts[1]
            if mingrelian and english:
                # Check if word appears as standalone in either mingrelian or english
                if _is_standalone_match(mingrelian, word) or _is_standalone_match(english, word):
                    standalone_output += "Mingrelian: " + mingrelian + "\n"
                    standalone_output += "English: " + english
                    standalone_output += "========\n"
                elif word in line:
                    # Word appears as substring
                    substring_output += "Mingrelian: " + mingrelian + "\n"
                    substring_output += "English: " + english
                    substring_output += "========\n"
    
    # Return standalone matches if found, otherwise substring matches
    if standalone_output != "========\n":
        return standalone_output, True
    elif substring_output != "========\n":
        return substring_output, False
    return "", False


# Russian
def grep_search_gal(word: str) -> tuple[str, bool]:
    """
    Search gal.tsv for Russian translations, prioritizing standalone word matches.
    Returns: (result_string, has_standalone_matches)
    """
    file_path = _get_data_path("gal.tsv")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return "", False
    
    # First pass: look for standalone word matches
    standalone_output = "========\n"
    substring_output = "========\n"
    
    for line in lines:
        parts = line.split("\t")
        if len(parts) >= 2:
            russian, mingrelian = parts[0], parts[1]
            if mingrelian and russian:
                # Check if word appears as standalone
                if _is_standalone_match(mingrelian, word) or _is_standalone_match(russian, word):
                    standalone_output += "Mingrelian: " + mingrelian
                    standalone_output += "Russian: " + russian + "\n"
                    standalone_output += "========\n"
                elif word in line or word.lower() in line:
                    # Word appears as substring
                    substring_output += "Mingrelian: " + mingrelian
                    substring_output += "Russian: " + russian + "\n"
                    substring_output += "========\n"
    
    # Return standalone matches if found, otherwise substring matches
    if standalone_output != "========\n":
        return standalone_output, True
    elif substring_output != "========\n":
        return substring_output, False
    return "", False


# Russian and Georgian
def grep_search_kk(word: str) -> tuple[str, bool]:
    """
    Search kk.tsv for Russian and Georgian translations, prioritizing standalone word matches.
    Returns: (result_string, has_standalone_matches)
    """
    file_path = _get_data_path("kk.tsv")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return "", False
    
    # First pass: look for standalone word matches
    standalone_output = "========\n"
    substring_output = "========\n"
    
    for line in lines:
        parts = line.split("\t")
        if len(parts) >= 4:
            mingrelian, ipa, russian, georgian = parts[0], parts[1], parts[2], parts[3]
            if mingrelian and russian and georgian:
                # Check if word appears as standalone
                if (_is_standalone_match(mingrelian, word) or 
                    _is_standalone_match(russian, word) or 
                    _is_standalone_match(georgian, word)):
                    standalone_output += "Mingrelian: " + mingrelian + "\n"
                    standalone_output += "Russian: " + russian + "\n"
                    standalone_output += "Georgian: " + georgian
                    standalone_output += "========\n"
                elif word in line or word.lower() in line:
                    # Word appears as substring
                    substring_output += "Mingrelian: " + mingrelian + "\n"
                    substring_output += "Russian: " + russian + "\n"
                    substring_output += "Georgian: " + georgian
                    substring_output += "========\n"
    
    # Return standalone matches if found, otherwise substring matches
    if standalone_output != "========\n":
        return standalone_output, True
    elif substring_output != "========\n":
        return substring_output, False
    return "", False


# Georgian
def grep_search_kajaia(word: str) -> str:
    """
    Search kajaia_cleaned.txt for Georgian dictionary entries.
    Splits text by empty lines and returns the block containing the search term.
    Prioritizes standalone word matches over substring matches.
    """
    file_path = _get_data_path("kajaia_cleaned.txt")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            kajaia_text = file.read()
    except FileNotFoundError:
        return ""
    
    entries = re.split(r'\n\s*\n', kajaia_text.strip())
    
    # First pass: look for standalone word matches
    standalone_output = "========\n"
    substring_output = "========\n"
    
    for entry in entries:
        if _is_standalone_match(entry, word):
            # Standalone match found
            standalone_output += entry.strip()
            standalone_output += "\n========\n"
        elif word in entry:
            # Substring match
            substring_output += entry.strip()
            substring_output += "\n========\n"
    
    # Return standalone matches if found, otherwise substring matches
    if standalone_output != "========\n":
        return standalone_output
    elif substring_output != "========\n":
        return substring_output
    return ""


def grep_search_from_english(word: str) -> str:
    """
    Search all dictionaries from English word.
    Short-circuits kajaia search if standalone matches found in extractive dictionaries.
    """
    # Try to translate to Russian and Georgian for broader search
    res_ru = word
    res_ge = word
    
    if GoogleTranslator is not None:
        try:
            res_ru = GoogleTranslator(source='en', target='ru').translate(word)
            res_ge = GoogleTranslator(source='en', target='ka').translate(word)
        except Exception:
            pass  # Fall back to original word if translation fails
    
    output = f"\nResults for {word}:\n"
    
    # Run extractive dictionary searches
    pairs_result, pairs_has_standalone = grep_search_pairs(word)
    gal_result, gal_has_standalone = grep_search_gal(res_ru)
    kk_ru_result, kk_ru_has_standalone = grep_search_kk(res_ru)
    kk_ge_result, kk_ge_has_standalone = grep_search_kk(res_ge)
    
    output += pairs_result
    output += gal_result
    output += kk_ru_result
    output += kk_ge_result
    
    # Only search kajaia if no standalone matches found in extractive dictionaries
    has_any_standalone = (pairs_has_standalone or gal_has_standalone or 
                          kk_ru_has_standalone or kk_ge_has_standalone)
    
    if not has_any_standalone:
        output += grep_search_kajaia(res_ge)

    if len(output) > 10000:
        return output[:10000]

    return output


def grep_search_from_mingrelian(word: str) -> str:
    """
    Search all dictionaries from Mingrelian word.
    Short-circuits kajaia search if standalone matches found in extractive dictionaries.
    """
    output = f"\nResults for {word}:\n"
    
    # Run extractive dictionary searches
    pairs_result, pairs_has_standalone = grep_search_pairs(word)
    gal_result, gal_has_standalone = grep_search_gal(word)
    kk_result, kk_has_standalone = grep_search_kk(word)
    
    output += pairs_result
    output += gal_result
    output += kk_result
    
    # Only search kajaia if no standalone matches found in extractive dictionaries
    has_any_standalone = pairs_has_standalone or gal_has_standalone or kk_has_standalone
    
    if not has_any_standalone:
        output += grep_search_kajaia(word)

    if len(output) > 10000:
        return output[:10000]
    
    return output


def grep_search_from_georgian(word: str) -> str:
    """
    Search all dictionaries from Georgian word.
    Short-circuits kajaia search if standalone matches found in extractive dictionaries.
    """
    # Try to translate to English and Russian for broader search
    res_en = word
    res_ru = word
    
    if GoogleTranslator is not None:
        try:
            res_en = GoogleTranslator(source='ka', target='en').translate(word)
            res_ru = GoogleTranslator(source='ka', target='ru').translate(word)
        except Exception:
            pass  # Fall back to original word if translation fails

    output = f"\nResults for {word}:\n"
    
    # Run extractive dictionary searches
    pairs_result, pairs_has_standalone = grep_search_pairs(res_en)
    kk_result, kk_has_standalone = grep_search_kk(word)
    gal_result, gal_has_standalone = grep_search_gal(res_ru)
    
    output += pairs_result
    output += kk_result
    output += gal_result
    
    # Only search kajaia if no standalone matches found in extractive dictionaries
    has_any_standalone = pairs_has_standalone or kk_has_standalone or gal_has_standalone
    
    if not has_any_standalone:
        output += grep_search_kajaia(word)

    if len(output) > 10000:
        return output[:10000]
    return output


def _load_grammar(path: Optional[str] = None) -> str:
    """Load the Mingrelian grammar file."""
    if path is None:
        path = _get_data_path("harris.txt")
    
    try:
        with open(path, "r", encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return ""


def _build_dict_entries(sentence: str, lookup_fn: Callable[[str], str]) -> str:
    """Build dictionary entries by looking up each word in the sentence."""
    dict_entries = ""
    for word in sentence.split():
        cleaned_word = word.strip(string.punctuation)
        if cleaned_word:
            dict_entries += lookup_fn(cleaned_word)
    return dict_entries


def _construct_translation_prompt(
    *,
    input_lang: str,
    output_lang: str,
    sentence: str,
    dict_entries: str,
    grammar: str,
) -> str:
    """Construct the complete translation prompt for a single LLM call."""
    in_label = LANG_LABEL.get(input_lang, input_lang)
    out_label = LANG_LABEL.get(output_lang, output_lang)

    # Build the base prompt
    prompt = f'''Your task is to translate a phrase or a sentence from {in_label} to {out_label}.

To accomplish this, I will provide you with a set of dictionary entries from Mingrelian dictionaries of different kinds.

The dictionary may have definitions in Russian, Georgian, or English.'''
    
    # Only add grammar section if we have grammar content
    if grammar:
        prompt += f''' I will also provide you with Mingrelian grammar information, describing the morphological and syntactual patterns of Mingrelian.'''
    
    prompt += f'''

Please use these resources to aid you in your translation.

You will translate the following phrase/sentence: "{sentence}". Return any notes you want, then end with:
<<<TRANSLATION>>>
FINAL_TRANSLATION_HERE
<<<END_TRANSLATION>>>

Here are some various dictionary entries for word(s) in that phrase:

{dict_entries}
'''
    
    # Only add grammar if we have it
    if grammar:
        prompt += f'''
Here is the Mingrelian grammar information:

{grammar}

That is the end of the grammar information.
'''
    
    prompt += f'''
Now remember, we are translating the following sentence: "{sentence}" from {in_label} to {out_label}.

Return any notes you want, then end with:
<<<TRANSLATION>>>
FINAL_TRANSLATION_HERE
<<<END_TRANSLATION>>>
'''
    
    return prompt


def _construct_prompt(
    sentence: str, 
    *, 
    input_lang: str, 
    output_lang: str, 
    lookup_fn: Callable[[str], str]
) -> str:
    """Construct a prompt for translation."""
    dict_entries = _build_dict_entries(sentence, lookup_fn)
    
    # Only load the massive grammar file if we actually have dictionary entries
    # Otherwise use simplified prompt (saves ~96K tokens and 40+ seconds!)
    if dict_entries and dict_entries.strip():
        grammar = _load_grammar()
    else:
        grammar = ""
    
    return _construct_translation_prompt(
        input_lang=input_lang,
        output_lang=output_lang,
        sentence=sentence,
        dict_entries=dict_entries,
        grammar=grammar,
    )


def construct_prompt_from_mingrelian_to_english(mingrelian_sentence: str) -> str:
    """Construct prompt for Mingrelian → English translation."""
    return _construct_prompt(
        mingrelian_sentence,
        input_lang="mingrelian",
        output_lang="english",
        lookup_fn=grep_search_from_mingrelian,
    )


def construct_prompt_from_english_to_mingrelian(english_sentence: str) -> str:
    """Construct prompt for English → Mingrelian translation."""
    return _construct_prompt(
        english_sentence,
        input_lang="english",
        output_lang="mingrelian",
        lookup_fn=grep_search_from_english,
    )


def construct_prompt_from_georgian_to_mingrelian(georgian_sentence: str) -> str:
    """Construct prompt for Georgian → Mingrelian translation."""
    return _construct_prompt(
        georgian_sentence,
        input_lang="georgian",
        output_lang="mingrelian",
        lookup_fn=grep_search_from_georgian,
    )


def construct_prompt_from_mingrelian_to_georgian(mingrelian_sentence: str) -> str:
    """Construct prompt for Mingrelian → Georgian translation."""
    return _construct_prompt(
        mingrelian_sentence,
        input_lang="mingrelian",
        output_lang="georgian",
        lookup_fn=grep_search_from_mingrelian,
    )


# Prompt builder routing
PROMPT_BUILDERS = {
    ("mingrelian", "english"): construct_prompt_from_mingrelian_to_english,
    ("english", "mingrelian"): construct_prompt_from_english_to_mingrelian,
    ("mingrelian", "georgian"): construct_prompt_from_mingrelian_to_georgian,
    ("georgian", "mingrelian"): construct_prompt_from_georgian_to_mingrelian,
}


def check_exact_match_simple(input_text: str, source_lang: str, target_lang: str) -> Optional[str]:
    """
    Check if the exact input text exists in extractive dictionaries (not kajaia).
    Returns the translation if found, None otherwise.
    
    This is the simple direct lookup without Google Translate augmentation.
    """
    input_lower = input_text.lower().strip()
    
    # Check sentence_pairs.tsv (Mingrelian ↔ English)
    if (source_lang, target_lang) in [("mingrelian", "english"), ("english", "mingrelian")]:
        try:
            file_path = _get_data_path("sentence_pairs.tsv")
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split("\t")
                    if len(parts) >= 2:
                        mingrelian, english = parts[0].strip(), parts[1].strip()
                        if source_lang == "mingrelian" and mingrelian.lower() == input_lower:
                            return english
                        elif source_lang == "english" and english.lower() == input_lower:
                            return mingrelian
        except FileNotFoundError:
            pass
    
    # Check kk.tsv (Mingrelian ↔ Russian ↔ Georgian)
    try:
        file_path = _get_data_path("kk.tsv")
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split("\t")
                if len(parts) >= 4:
                    mingrelian, ipa, russian, georgian = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
                    
                    # Mingrelian → Georgian
                    if source_lang == "mingrelian" and target_lang == "georgian":
                        if mingrelian.lower() == input_lower:
                            return georgian
                    
                    # Georgian → Mingrelian
                    elif source_lang == "georgian" and target_lang == "mingrelian":
                        if georgian.lower() == input_lower:
                            return mingrelian
                    
                    # Mingrelian → English
                    elif source_lang == "mingrelian" and target_lang == "english":
                        if mingrelian.lower() == input_lower:
                            # We don't have English in kk, skip
                            pass
    except FileNotFoundError:
        pass
    
    # Check gal.tsv (Russian ↔ Mingrelian)
    try:
        file_path = _get_data_path("gal.tsv")
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    russian, mingrelian = parts[0].strip(), parts[1].strip()
                    
                    # Russian → Mingrelian
                    if source_lang == "russian" and target_lang == "mingrelian":
                        if russian.lower() == input_lower:
                            return mingrelian
                    
                    # Mingrelian → Russian
                    elif source_lang == "mingrelian" and target_lang == "russian":
                        if mingrelian.lower() == input_lower:
                            return russian
    except FileNotFoundError:
        pass
    
    return None


def find_mingrelian_in_dicts(text: str) -> Optional[tuple[str, str]]:
    """
    Find ANY translation for a text in dictionaries, searching across all columns.
    Returns (mingrelian, other_language_text, other_language_code) if found.
    
    Search order prioritizes clean extractive dictionaries (sentence_pairs, gal) over kk.
    
    Args:
        text: Text to search for (case-insensitive)
        
    Returns:
        tuple or None: (mingrelian_text, other_lang_text, lang_code) if found
    """
    text_lower = text.lower().strip()
    
    # Priority 1: Search sentence_pairs.tsv (English ↔ Mingrelian, cleanest)
    try:
        file_path = _get_data_path("sentence_pairs.tsv")
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    mingrelian, english = parts[0].strip(), parts[1].strip()
                    if mingrelian.lower() == text_lower:
                        return (mingrelian, english, "en")
                    elif english.lower() == text_lower:
                        return (mingrelian, english, "en")
    except FileNotFoundError:
        pass
    
    # Priority 2: Search gal.tsv (Russian ↔ Mingrelian, reliable)
    try:
        file_path = _get_data_path("gal.tsv")
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    russian, mingrelian = parts[0].strip(), parts[1].strip()
                    if mingrelian.lower() == text_lower:
                        return (mingrelian, russian, "ru")
                    elif russian.lower() == text_lower:
                        return (mingrelian, russian, "ru")
    except FileNotFoundError:
        pass
    
    # Priority 3: Search kk.tsv (may have data quality issues, use as fallback)
    try:
        file_path = _get_data_path("kk.tsv")
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split("\t")
                if len(parts) >= 4:
                    mingrelian, ipa, russian, georgian = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
                    if mingrelian.lower() == text_lower:
                        # Found mingrelian, prefer Georgian
                        return (mingrelian, georgian, "ka")
                    elif georgian.lower() == text_lower:
                        return (mingrelian, georgian, "ka")
                    elif russian.lower() == text_lower:
                        return (mingrelian, russian, "ru")
    except FileNotFoundError:
        pass
    
    return None


def check_exact_match_with_google_translate(input_text: str, source_lang: str, target_lang: str) -> Optional[str]:
    """
    Advanced exact match using Google Translate to bridge high-resource languages.
    
    SCENARIO 1: Translating TO Mingrelian (from English/Georgian)
    - Translate input to all high-resource languages (en, ka, ru)
    - Search dictionaries for each translated version
    - Return Mingrelian if found
    
    SCENARIO 2: Translating FROM Mingrelian (to English/Georgian)
    - Search dictionaries for Mingrelian word
    - If found with any high-resource language pair
    - Google Translate that language to target
    - Return translation
    """
    if GoogleTranslator is None:
        return None
    
    # SCENARIO 1: Translating TO Mingrelian from high-resource language
    if target_lang == "mingrelian" and source_lang in ["english", "georgian"]:
        input_lower = input_text.lower().strip()
        
        # Try direct lookup first
        direct_match = check_exact_match_simple(input_text, source_lang, target_lang)
        if direct_match:
            return direct_match
        
        # Translate to other high-resource languages and search
        translations_to_try = [(input_text, source_lang)]  # Start with original
        
        try:
            # Translate to other languages
            if source_lang == "english":
                # en → ka, en → ru
                ka_trans = GoogleTranslator(source="en", target="ka").translate(input_text)
                ru_trans = GoogleTranslator(source="en", target="ru").translate(input_text)
                translations_to_try.extend([(ka_trans, "georgian"), (ru_trans, "russian")])
            
            elif source_lang == "georgian":
                # ka → en, ka → ru
                en_trans = GoogleTranslator(source="ka", target="en").translate(input_text)
                ru_trans = GoogleTranslator(source="ka", target="ru").translate(input_text)
                translations_to_try.extend([(en_trans, "english"), (ru_trans, "russian")])
        
        except Exception:
            pass  # If translation fails, continue with what we have
        
        # Search for each translated version in dictionaries
        for translated_text, lang in translations_to_try:
            match = check_exact_match_simple(translated_text, lang, "mingrelian")
            if match:
                print(f"[GOOGLE BRIDGE TO MINGRELIAN] {input_text} ({source_lang}) → {translated_text} ({lang}) → {match} (mingrelian)")
                return match
    
    # SCENARIO 2: Translating FROM Mingrelian to high-resource language
    elif source_lang == "mingrelian" and target_lang in ["english", "georgian"]:
        # Try direct lookup first
        direct_match = check_exact_match_simple(input_text, source_lang, target_lang)
        if direct_match:
            return direct_match
        
        # Search for Mingrelian in ANY dictionary with ANY language pair
        result = find_mingrelian_in_dicts(input_text)
        if result:
            mingrelian_text, other_lang_text, lang_code = result
            
            # If the found language IS the target, return directly
            lang_map = {"en": "english", "ka": "georgian", "ru": "russian"}
            found_lang = lang_map.get(lang_code)
            
            if found_lang == target_lang:
                print(f"[DIRECT DICT MATCH] {mingrelian_text} (mingrelian) → {other_lang_text} ({target_lang})")
                return other_lang_text
            
            # Otherwise, Google Translate from found language to target
            try:
                if target_lang == "english":
                    target_code = "en"
                elif target_lang == "georgian":
                    target_code = "ka"
                else:
                    return None
                
                translated = GoogleTranslator(source=lang_code, target=target_code).translate(other_lang_text)
                print(f"[GOOGLE BRIDGE FROM MINGRELIAN] {mingrelian_text} (mingrelian) → {other_lang_text} ({lang_code}) → {translated} ({target_code})")
                return translated
            
            except Exception as e:
                print(f"[GOOGLE BRIDGE ERROR] Failed to translate: {e}")
                pass
    
    return None


def extract_translation(response_text: str) -> str:
    """
    Extract the final translation from LLM response using <<<TRANSLATION>>> markers.
    
    Args:
        response_text: The model's response text
        
    Returns:
        str: The extracted translation, or the full response if markers not found
    """
    # Look for content between <<<TRANSLATION>>> and <<<END_TRANSLATION>>>
    match = re.search(r'<<<TRANSLATION>>>\s*(.*?)\s*<<<END_TRANSLATION>>>', 
                     response_text, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    # Fallback: return the full response if markers not found
    return response_text.strip()


def translate(
    input_text: str,
    source_lang: str,
    target_lang: str,
    llm_client
) -> dict:
    """
    Translate text using single LLM call approach.
    
    Args:
        input_text: Text to translate
        source_lang: Source language (mingrelian, georgian, or english)
        target_lang: Target language (mingrelian, georgian, or english)
        llm_client: LLM client instance
        
    Returns:
        dict: Translation results with keys: translation, full_response
    """
    overall_start = time.time()
    
    # OPTIMIZATION 1: Check for exact match with Google Translate bridge
    stage_start = time.time()
    exact_match = check_exact_match_with_google_translate(input_text, source_lang, target_lang)
    log_stage_timing(logger, "Google Translate Bridge Check", time.time() - stage_start)
    
    if exact_match is not None:
        log_stage_timing(logger, "TOTAL (instant lookup)", time.time() - overall_start, "✅ No LLM call")
        logger.info(f"Instant lookup: '{input_text}' ({source_lang}) → '{exact_match}' ({target_lang})")
        log_instant_lookup(logger, input_text, exact_match, "dictionary+google_translate")
        return {
            'translation': exact_match,
            'full_response': f"Dictionary match (via Google Translate bridge):\n{exact_match}"
        }
    
    logger.info(f"No instant lookup found, proceeding to LLM for '{input_text}' ({source_lang} → {target_lang})")
    
    # OPTIMIZATION 2: Handle Georgian ↔ English with Google Translate (no Mingrelian involved)
    if GoogleTranslator is not None:
        if source_lang == "english" and target_lang == "georgian":
            stage_start = time.time()
            translation = GoogleTranslator(source="en", target="ka").translate(input_text)
            log_stage_timing(logger, "Google Translate Direct", time.time() - stage_start)
            log_stage_timing(logger, "TOTAL (Google Translate)", time.time() - overall_start, "✅ No LLM call")
            log_instant_lookup(logger, input_text, translation, "google_translate_en_ka")
            return {
                'translation': translation,
                'full_response': f"Translation (via Google Translate):\n{translation}"
            }
        
        if source_lang == "georgian" and target_lang == "english":
            stage_start = time.time()
            translation = GoogleTranslator(source="ka", target="en").translate(input_text)
            log_stage_timing(logger, "Google Translate Direct", time.time() - stage_start)
            log_stage_timing(logger, "TOTAL (Google Translate)", time.time() - overall_start, "✅ No LLM call")
            log_instant_lookup(logger, input_text, translation, "google_translate_ka_en")
            return {
                'translation': translation,
                'full_response': f"Translation (via Google Translate):\n{translation}"
            }
    
    # Get the appropriate prompt builder
    builder = PROMPT_BUILDERS.get((source_lang, target_lang))
    if builder is None:
        raise ValueError(f"Unsupported translation direction: {source_lang} → {target_lang}")
    
    # Build the prompt (includes dictionary searches)
    stage_start = time.time()
    prompt = builder(input_text)
    log_stage_timing(logger, "Prompt Construction (with dictionary searches)", time.time() - stage_start)
    log_prompt(logger, prompt, source_lang, target_lang)
    
    # Call the LLM - THIS IS THE KEY TIMING
    stage_start = time.time()
    response = llm_client.complete(prompt)
    llm_time = time.time() - stage_start
    log_stage_timing(logger, "🔥 LLM API CALL", llm_time, f"provider={llm_client.provider}, model={llm_client.model}")
    log_llm_response(logger, response, source_lang, target_lang)
    
    # Extract the translation
    stage_start = time.time()
    translation = extract_translation(response)
    log_stage_timing(logger, "Response Extraction", time.time() - stage_start)
    
    total_time = time.time() - overall_start
    log_stage_timing(logger, "TOTAL (with LLM)", total_time, f"LLM={llm_time:.3f}s ({llm_time/total_time*100:.1f}%)")
    
    logger.info(f"Extracted translation: '{translation}'")
    
    return {
        'translation': translation,
        'full_response': response
    }
