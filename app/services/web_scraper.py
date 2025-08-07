# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin

# BASE_URL = "https://worldlink.com.np/career/"

# def scrape_vacancies():
#     vacancies = []

#     for page_num in [1, 2]:
#         url = f"{BASE_URL}?page={page_num}"  # correct URL
#         response = requests.get(url)
#         response.raise_for_status()

#         soup = BeautifulSoup(response.text, "html.parser")

#         # FIX SELECTOR after inspecting the page
#         job_cards = soup.select("div.career-item a")

#         for job in job_cards:
#             title = job.get_text(strip=True)
#             link = job.get("href")

#             if link and not link.startswith("http"):
#                 link = "https://worldlink.com.np" + link

#             vacancies.append({"title": title, "link": link})

#     return vacancies

# # def scrape_vacancies():
# #     """
# #     Scrapes job vacancies from WorldLink career page.
# #     Returns list of dicts: [{'title': str, 'link': str, 'description': str}]
# #     """
# #     url = f"{BASE_URL}/career/"
# #     response = requests.get(url, timeout=10)
# #     response.raise_for_status()

# #     soup = BeautifulSoup(response.text, "html.parser")
# #     vacancies = []

# #     # Select all vacancy links
# #     job_cards = [a for a in soup.find_all('a') if 'vacancy' in a.get_text(strip=True).lower() or 'job' in a.get_text(strip=True).lower()]

# #     print(f"Filtered job cards found: {len(job_cards)}")
# #     for card in job_cards:
# #         print(card.get_text(strip=True), card.get("href"))


# #     for card in job_cards:
# #         title = card.get_text(strip=True)
# #         link = urljoin(BASE_URL, card.get("href"))
# #         description = scrape_job_description(link)

# #         vacancies.append({
# #             "title": title,
# #             "link": link,
# #             "description": description
# #         })

# #     return vacancies


# # def scrape_job_description(link: str) -> str:
# #     """
# #     Scrapes detailed job description from a job page.
# #     """
# #     resp = requests.get(link, timeout=10)
# #     resp.raise_for_status()

# #     soup = BeautifulSoup(resp.text, "html.parser")
# #     desc_container = soup.select_one(".career-details") or soup

# #     description = desc_container.get_text(separator="\n", strip=True)

# #     return description

import requests
from bs4 import BeautifulSoup
from typing import List, Dict

BASE_URL = "https://worldlink.com.np/career/page/{page}/?page"

def scrape_worldlink_jobs() -> List[Dict]:
    """
    Scrape job vacancies (title, deadline, URL, description) from WorldLink Career pages.
    """
    jobs = []

    for page in range(1, 3):  # Scraping 2 pages
        url = BASE_URL.format(page=page)
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        job_cards = soup.find_all("div", class_="career-card")

        for card in job_cards:
            # Extract title
            title_tag = card.find("span", class_="career-card__title")
            title = title_tag.get_text(strip=True) if title_tag else "No title"

            # Extract deadline
            deadline_tag = card.find("p", class_="career-card__date")
            deadline = (
                deadline_tag.get_text(strip=True).replace("Deadline:", "").strip()
                if deadline_tag else "Not mentioned"
            )

            # Extract detail link
            link_tag = card.find("a", href=True)
            detail_link = link_tag["href"] if link_tag else None

            if not detail_link:
                continue

            if not detail_link.startswith("http"):
                detail_link = "https://worldlink.com.np" + detail_link

            # Scrape job description
            description = scrape_job_description(detail_link)

            jobs.append({
                "title": title,
                "deadline": deadline,
                "url": detail_link,
                "description": description
            })

    return jobs


def scrape_job_description(detail_url: str) -> str:
    """
    Visit job detail page and extract full description text.
    """
    try:
        response = requests.get(detail_url, timeout=10)
        if response.status_code != 200:
            return "Description not available"

        soup = BeautifulSoup(response.text, "html.parser")

        # Try multiple possible description containers
        description_tag = (
            soup.find("div", class_="career-details")
            or soup.find("div", class_="job-description")
            or soup.find("div", class_="career-card__detail")
        )

        return description_tag.get_text(separator="\n", strip=True) if description_tag else "Description not available"

    except Exception as e:
        return f"Error fetching description: {e}"
