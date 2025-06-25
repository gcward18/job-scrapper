import requests
import json
from bs4 import BeautifulSoup
from html import unescape
import textwrap
import os
from groq import Groq

# Initialize Groq client
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)
API_URL = "https://gcsservices.careers.microsoft.com/search/api/v1/search"

params = {
    "lc": [
        "Seattle, Washington, United States",
        "Mountain View, California, United States",
        "Palo Alto, California, United States"
    ],
    "d": "Software Engineering",
    "rt": "Individual Contributor",
    "l": "en_us",
    "pg": 1,
    "pgSz": 20,
    "o": "Relevance",
    "flt": "true"
}


headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

def strip_html(html_string):
    """Remove HTML tags and decode HTML entities."""
    return BeautifulSoup(unescape(html_string), "html.parser").get_text(separator=" ")

def fetch_jobs(url:str):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return

    jobs = response.json()["operationResult"]["result"]["jobs"]
    return jobs

def fetch_job(url:str):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return

    job = response.json()["operationResult"]["result"]
    return job

def save_job_locally(write_path: str, jobs: list[any]):
    with open(write_path, 'w') as file_out:
        for i, job in enumerate(jobs, start=1):
            jobId = job["jobId"]
            title = job["title"]
            location = job["properties"].get("primaryLocation", "N/A")
            posting_date = job.get("postingDate", "")[:10]
            role_type = job["properties"].get("roleType", "N/A")
            job_type = job["properties"].get("jobType", "N/A")
            flexibility = job["properties"].get("workSiteFlexibility", "N/A")
            desc = strip_html(job["properties"].get("description", ""))[:300] + "..."

            file_out.writelines(f"\n{i}. {title}\n")
            file_out.writelines(f"   Job Id:          : {jobId}\n")
            file_out.writelines(f"   Location         : {location}\n")
            file_out.writelines(f"   Posted on        : {posting_date}\n")
            file_out.writelines(f"   Role Type        : {role_type}\n")
            file_out.writelines(f"   Job Type         : {job_type}\n")
            file_out.writelines(f"   Work Flexibility : {flexibility}\n")
            file_out.writelines(f"   Description      :\n")
            file_out.writelines(textwrap.fill(desc, width=80, initial_indent="      ", subsequent_indent="      "))
            file_out.writelines('\n')

            file_out.writelines("-" * 80)
            file_out.writelines('\n')
            
def save_focused_job_locally(write_path: str, job: any):
    job_str = []
    
    with open(write_path, 'w') as file_out:
        jobId = job["jobId"]
        title = job["title"]
        desc = strip_html(job["description"]) + "..."
        qual = strip_html(job["qualifications"]) + "..."

        job_str.append(f"\n{title}\n")
        job_str.append(f"   Job Id:          : {jobId}\n")
        job_str.append(f"   Description      :\n")
        job_str.append(textwrap.fill(desc, width=80, initial_indent="      ", subsequent_indent="      "))
        job_str.append(textwrap.fill(qual, width=80, initial_indent="      ", subsequent_indent="      "))
        job_str.append('\n')

        job_str.append("-" * 80)
        job_str.append('\n')

        for line in job_str:
            file_out.writelines(line)
    
    return ''.join(job_str)

def find_best_fits():
    contents = ""
    resume = ""
    
    with open("results/ms-jobs.txt", "r") as file_in:
        contents = ''.join(file_in.readlines())
    with open("sources/resume.txt", "r") as file_in:
        resume = ''.join(file_in.readlines())
        
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": (
                        f"""
                        Find the best jobs for me based on my resume (start of resume begins at RESUME START and ends on RESUME END) the jobs are posted after 
                        Starting when you see JOBS START
                        after finding these jobs create them as links and store them as a json list each item in the list should be formatted as 
                        https://gcsservices.careers.microsoft.com/search/api/v1/job/'Job Id'?lang=en_us
                        
                        where 'Job Id' is the job id that was in the JOBS list for a particular job example output would be
                        ["https://gcsservices.careers.microsoft.com/search/api/v1/job/1820515?lang=en_us"]
                        if only one match, they should have an 85% match to be made in the list
                        do not return anything other than the requested output created from the jobs list, do not add any new lines, or extra formatting, just the list
                        do not add any text explaining why you selected these jobs
                        RESUME START
                        {resume}
                        RESUME END
                        
                        JOBS START
                        {contents}
                        """

                    )
                },
            ]
        }
    ]
    
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=messages,
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    
    response_content = completion.choices[0].message.content
    return response_content    


def check_match(job):
    contents = ""
    resume = ""
    with open("sources/resume.txt", "r") as file_in:
        resume = ''.join(file_in.readlines())
    with open(f"results/{job['jobId']}.txt", "r") as file_in:
        contents = ''.join(file_in.readlines())
        
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": (
                        f"""
                        Based on my resume (start of resume begins at RESUME START and ends on RESUME END) the jobs are posted after 
                        Starting when you see JOBS START
                        I am looking for Software Engineer
                            Full-Stack Developer, Backend Developer, or Product Engineer at top tech companies and
                            startups, strongly prefer Location: Raliegh, NC Cary, NC Seattle, WA Sunnyvale, CA Mountain
                            View, CA Austin, TX San Fancisco, CA Dallas, TX San Diego, CA with a 140-200k total
                            compensation. avoid applying this Smaller companies &lt; 50 employees call me out when you
                            notice this.
                            Job Focus: Target Software Engineer, Full-Stack Developer, Backend Developer, or Product
                            Engineer roles at tech companies with 50+ employees, and note I am open to relocation
                            Never use em dashes in any generated text!
                            Avoid using the sentence structure “Whether that’s (a, b, or c), I…”
                            I would like you to do an evaluation of a job based on my resume and job description and output
                            the results as a nice table.
                            Please be critical. If I am missing key qualifications on my resume, please clearly call these out,
                            and indicate that the role is not a fit.
                            -Please only say jobs where I 100% exceed all requirements are good fits. Also, if the job is
                            remote it&#39;s probably not a great fit. but I am open for relocation with a big tech companies.
                            Output:
                            - Fit for role
                            - Match to minimum qualifications
                            - Match to preferred qualifications
                            - Estimated compensation
                            - Remote policy
                            - Overall fit


                            SAMPLE PROMPT RESULT:

                            https://fa-evlf-
                            saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/3279
                            8/?utm_medium=jobshare&amp;utm_source=External+Job+Share

                            Job Fit Evaluation – Hertz Senior Software Engineer
                            Category Evaluation
                            Fit for Role ✅ Strong fit
                            ✅ Match to Minimum Qualifications

                            ✔ Meets and exceeds – You have 4+ years of experience, a B.S. in CS, and
                            extensive software engineering background.

                            ✅ Match to Preferred Qualifications

                            ✔ Fully meets – You’ve led teams, delivered full-stack solutions, and
                            worked across frontend/backend at scale.

                            Estimated Compensation $150,000–$180,000 base + bonus + profit sharing (✅ in your $140–200k

                            range)

                            Remote Policy On-site (San Francisco, CA or Estero, FL) – ✅ SF is on your target location

                            list

                            ⭐ Overall Fit ✅ Very strong fit – Meets all job and compensation requirements; well-

                            aligned with your career trajectory

                            ✅ Summary Recommendation
                            ✅
                            Proceed? ✅ Yes – Strong Match

                            Why?

                            You meet and exceed all stated qualifications. The compensation is in your desired range,
                            the location is acceptable, the company is large and reputable, and the role gives you room
                            to continue leading technically while growing impact.
                            
                        RESUME START
                        {resume}
                        RESUME END
                        
                        JOBS START
                        {contents}
                        """

                    )
                },
            ]
        }
    ]
    
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=messages,
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    
    response_content = completion.choices[0].message.content
    return response_content    

   
if __name__ == "__main__":
    jobs = fetch_jobs(API_URL)
    save_job_locally('results/ms-jobs.txt', jobs)
    serialized_jobs = find_best_fits()
    with open('results/best-matches', 'w') as file_out:
        file_out.writelines(serialized_jobs)
    with open('results/best-matches', 'r') as file_in:
        serialized_jobs = ''.join(file_in.readlines())
    job_list = json.loads(serialized_jobs)
    
    for job_url in job_list:
        job = fetch_job(job_url)
        save_focused_job_locally(f"results/{job['jobId']}.txt", job=job)
        results = check_match(job)
        strong_fit = 'Very strong fit' in results or 'Proceed? Yes' in results
        with open(f"{'strong-matches' if strong_fit else 'other-matches'}/{job['jobId']}-results.md", 'w') as file_out:
            file_out.writelines(results)
     
    