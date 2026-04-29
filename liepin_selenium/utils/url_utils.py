import re


def extract_job_info_from_url(job_url):
    """
    Extract short_url and job_id from a Liepin job URL.

    :param job_url: Full job URL from Liepin
    :type job_url: str
    :return: Tuple of (short_url, job_id)
    :rtype: tuple
    """
    short_url = job_url
    job_id = ""

    if not job_url:
        return short_url, job_id

    # Extract base URL without query parameters (supports both /a/ and /job/ patterns)
    match = re.match(r"(https://www\.liepin\.com/(?:a|job)/\d+\.shtml)", job_url)
    if match:
        short_url = match.group(1)
        # Extract job_id from short_url
        id_match = re.search(r"/(\d+)\.shtml", short_url)
        if id_match:
            job_id = id_match.group(1)

    return short_url, job_id
