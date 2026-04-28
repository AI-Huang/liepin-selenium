from bs4 import BeautifulSoup

from config import JOB_CARD_CLASS


class JobParser:
    @staticmethod
    def parse(html):
        soup = BeautifulSoup(html, "html.parser")
        job_cards = soup.find_all("div", class_=JOB_CARD_CLASS)
        return job_cards

    @staticmethod
    def extract_job_info(card):
        job_link = card.find("a")
        if not job_link:
            return None

        job_url = job_link.get("href")
        job_text = job_link.text.strip()

        # 提取地点
        location_start = job_text.find("【")
        location_end = job_text.find("】")
        location = (
            job_text[location_start + 1 : location_end]
            if (location_start != -1 and location_end != -1)
            else ""
        )

        # 提取职位标题
        job_title = job_text[:location_start] if location_start != -1 else job_text

        # 提取薪资
        salary_start = location_end + 1 if location_end != -1 else 0
        salary_end = job_text.find("k", salary_start)
        salary = ""
        if salary_end != -1:
            for j in range(salary_start, salary_end):
                if job_text[j].isdigit() or job_text[j] == "-":
                    salary_start = j
                    break
            salary = job_text[salary_start : salary_end + 1]

        # 提取工作经验
        exp_start = salary_end + 1 if salary_end != -1 else 0
        exp_end = job_text.find("年", exp_start)
        experience = ""
        if exp_end != -1:
            for j in range(exp_start, exp_end):
                if job_text[j].isdigit() or job_text[j] in ["经", "验", "不", "限"]:
                    exp_start = j
                    break
            experience = job_text[exp_start : exp_end + 1]

        # 提取学历要求
        edu_start = exp_end + 1 if exp_end != -1 else 0
        education = job_text[edu_start:].strip()

        return {
            "title": job_title,
            "location": location,
            "salary": salary,
            "experience": experience,
            "education": education,
            "url": job_url,
        }