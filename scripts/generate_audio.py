#!/usr/bin/env python3
"""Generate a natural-sounding English Tech Brief episode with Kokoro."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--voice", default="af_heart")
    args = parser.parse_args()

    text = args.input.read_text(encoding="utf-8")
    pipeline = KPipeline(lang_code="a")
    chunks: list[np.ndarray] = []
    pause = np.zeros(6_000, dtype=np.float32)
    for _, _, audio in pipeline(text, voice=args.voice):
        chunks.extend((audio, pause))
    if not chunks:
        raise RuntimeError("Kokoro produced no audio.")
    sf.write(args.output, np.concatenate(chunks), 24_000)


if __name__ == "__main__":
    main()
