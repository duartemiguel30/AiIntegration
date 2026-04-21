import logging
import requests
from config import NVD_API_URL, NVD_RESULTS_PER_PAGE

logger = logging.getLogger(__name__)


def fetch_security_data(results_per_page: int = NVD_RESULTS_PER_PAGE) -> list[dict]:
    url = f"{NVD_API_URL}?resultsPerPage={results_per_page}"
    logger.info("[FETCH] Requesting NVD API: %s", url)

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("[FETCH] Failed to contact NVD API: %s", e)
        raise

    data = response.json()
    vulnerabilities = data.get("vulnerabilities", [])

    items = []
    for vuln in vulnerabilities:
        cve = vuln.get("cve", {})

        descriptions = cve.get("descriptions", [])
        description = next(
            # se a língua for inglesa e existir descricao, pega no "value" seguinte
            (d["value"] for d in descriptions if d.get("lang") == "en"),
            "No description available.",
        )

        # CVSS score (v3.1 preferred, fallback v2)
        metrics = cve.get("metrics", {})
        cvss_score = None
        if "cvssMetricV31" in metrics:
            cvss_score = metrics["cvssMetricV31"][0]["cvssData"]["baseScore"]
        elif "cvssMetricV2" in metrics:
            cvss_score = metrics["cvssMetricV2"][0]["cvssData"]["baseScore"]

        items.append({
            "id": cve.get("id", "UNKNOWN"),
            "published": cve.get("published", ""),
            "description": description,
            "cvss_score": cvss_score,
        })

    logger.info("[FETCH] Retrieved %d vulnerabilities.", len(items))
    return items