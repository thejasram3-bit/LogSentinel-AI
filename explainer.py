# -*- coding: utf-8 -*-
"""explainer.py — Gemini LLM explanation function"""

import google.generativeai as genai  # type: ignore[import]
import hashlib
import json
import os
import streamlit as st

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
llm = genai.GenerativeModel("gemini-2.5-flash")

CACHE_FILE = "llm_cache.json"
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE) as f:
        _cache = json.load(f)
else:
    _cache = {}

EVENT_MEANINGS = {
    "E1":  "Receiving block (normal)",
    "E2":  "PacketResponder ending (normal)",
    "E3":  "Pipeline setup",
    "E4":  "Block transfer",
    "E5":  "Block received OK (normal)",
    "E6":  "Block report sent",
    "E7":  "Heartbeat sent",
    "E10": "Block already exists",
    "E11": "IOException ERROR — read/write failure",
    "E12": "Block not found",
    "E16": "Connection refused",
    "E17": "Replication failed",
    "E32": "Block corrupted",
    "E35": "DataNode unresponsive",
}

def explain_anomaly(block_id, event_list, prob):
    event_str = ",".join(event_list)
    cache_key = hashlib.md5(f"{block_id}_{event_str}_{round(prob,2)}".encode()).hexdigest()

    if cache_key in _cache:
        return _cache[cache_key]

    readable = "\n".join(f"{e}: {EVENT_MEANINGS.get(e, e)}" for e in event_list)

    prompt = f"""You are a server reliability expert analyzing HDFS logs.
ML model flagged this block as anomalous.

BLOCK ID: {block_id}
CONFIDENCE: {prob*100:.1f}%
EVENTS (in order):
{readable}

Reply in EXACTLY this format (no extra text):
WHAT IS HAPPENING: [one sentence for non-technical manager]
SEVERITY: [Low / Medium / High / Critical]
LIKELY CAUSE: [one technical sentence]
RECOMMENDED ACTION: [one specific action]
ESTIMATED IMPACT: [one sentence if ignored]"""

    try:
        resp = llm.generate_content(prompt)
        text = resp.text.strip()

        result = {
            "block_id": block_id,
            "confidence": f"{prob*100:.1f}%",
            "what": "", "severity": "High", "cause": "", "action": "", "impact": "",
            "raw": text
        }
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("WHAT IS HAPPENING:"): result["what"] = line.split(":",1)[1].strip()
            elif line.startswith("SEVERITY:"): result["severity"] = line.split(":",1)[1].strip()
            elif line.startswith("LIKELY CAUSE:"): result["cause"] = line.split(":",1)[1].strip()
            elif line.startswith("RECOMMENDED ACTION:"): result["action"] = line.split(":",1)[1].strip()
            elif line.startswith("ESTIMATED IMPACT:"): result["impact"] = line.split(":",1)[1].strip()

        _cache[cache_key] = result
        with open(CACHE_FILE, "w") as f:
            json.dump(_cache, f, indent=2)
        return result
        
    except Exception as e:
        return {
            "block_id":   block_id,
            "confidence": f"{prob*100:.1f}%",
            "what":    "Explanation delayed — API rate limit reached. Please wait a minute and try again.",
            "severity":"High",
            "cause":   f"Events: {event_str}",
            "action":  "Investigate manually",
            "impact":  "Potential data loss",
            "raw":     str(e)
        }

        
        