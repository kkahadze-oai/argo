import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple, Optional, Union

def eaf_to_parallel(
    eaf_path: Union[str, Path],
    source_tier_id: str = "A_phrase-txt-xmf",
    target_tier_id: str = "A_phrase-gls-en",
    write_tsv: Optional[Union[str, Path]] = None,
    normalize_ws: bool = True,
) -> List[Tuple[str, str]]:
    """
    Extract (source, translation) pairs from an ELAN .eaf file.

    Parameters
    ----------
    eaf_path        : path to the .eaf file.
    source_tier_id  : tier that contains the source-language text.
    target_tier_id  : tier that contains the translations (must be a REF tier).
    write_tsv       : optional path — if given, writes a tab-separated corpus.
    normalize_ws    : collapse repeated whitespace and strip leading / trailing space.

    Returns
    -------
    List of (source_sentence, target_sentence) tuples in file order.
    """
    eaf_path = Path(eaf_path)
    root = ET.parse(eaf_path).getroot()

    # 1) Build a map from source ANNOTATION_ID ➔ sentence
    src_tier = root.find(f".//TIER[@TIER_ID='{source_tier_id}']")
    if src_tier is None:
        raise ValueError(f"Source tier “{source_tier_id}” not found in {eaf_path.name}")

    id2src: dict[str, str] = {}
    for ann in src_tier.iter("ALIGNABLE_ANNOTATION"):
        txt = ann.find("ANNOTATION_VALUE")
        if txt is None or txt.text is None:
            continue
        sent = txt.text
        if normalize_ws:
            sent = re.sub(r"\s+", " ", sent).strip()
        id2src[ann.attrib["ANNOTATION_ID"]] = sent

    # 2) Collect translation pairs by following REF_ANNOTATION ➔ ANNOTATION_REF
    tgt_tier = root.find(f".//TIER[@TIER_ID='{target_tier_id}']")
    if tgt_tier is None:
        raise ValueError(f"Target tier “{target_tier_id}” not found in {eaf_path.name}")

    pairs: List[Tuple[str, str]] = []
    for ref_ann in tgt_tier.iter("REF_ANNOTATION"):
        parent_id = ref_ann.attrib.get("ANNOTATION_REF")
        tgt_val   = ref_ann.find("ANNOTATION_VALUE")
        if parent_id not in id2src or tgt_val is None or tgt_val.text is None:
            continue
        tgt_sent = tgt_val.text
        if normalize_ws:
            tgt_sent = re.sub(r"\s+", " ", tgt_sent).strip()
        pairs.append((id2src[parent_id], tgt_sent))

    # 3) Optionally write out a TSV file
    if write_tsv:
        write_tsv = Path(write_tsv)
        write_tsv.write_text("\n".join(f"{s}\t{t}" for s, t in pairs), encoding="utf-8")
        print(f"Wrote {len(pairs):,} sentence pairs to {write_tsv}")

    return pairs


if __name__ == "__main__":
    number = 10
    eaf_to_parallel(f"data/lobz/{number:04d}.eaf", write_tsv=f"data/lobz/{number:04d}.tsv")