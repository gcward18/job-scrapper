# Job Scraper & Resume Matcher

This project automates the process of scraping Microsoft job postings, evaluating them against your resume, and generating detailed fit analyses for each role. It leverages the Groq LLM API for intelligent matching and outputs structured results for easy review.

## Features

- **Job Scraping:** Fetches the latest job postings for software engineering roles in target locations.
- **Resume Parsing:** Reads your resume from `sources/resume.txt`.
- **AI-Powered Matching:** Uses Groq LLM to evaluate job fit based on your resume and job descriptions.
- **Result Categorization:** Outputs strong matches to `strong-matches/` and other matches to `other-matches/`.
- **Detailed Reports:** Generates Markdown reports with fit tables and recommendations for each job.
- **Best Matches List:** Stores top job URLs in `results/best-matches`.

## Project Structure

```
.
├── __init__.py
├── main.py
├── .env
├── results/
│   ├── ms-jobs.txt
│   ├── best-matches
│   └── <jobId>.txt
├── sources/
│   └── resume.txt
├── strong-matches/
│   └── <jobId>-results.md
├── other-matches/
│   └── <jobId>-results.md
└── .vscode/
    └── launch.json
```

## Setup

1. **Clone the repository**

2. **Install dependencies**
   ```sh
   pip install requests beautifulsoup4 groq
   ```

3. **Set up your environment**
   - Add your Groq API key to `.env`:
     ```
     GROQ_API_KEY="your_groq_api_key"
     ```

4. **Add your resume**
   - Place your resume text in `sources/resume.txt`.

## Usage

Run the main script to fetch jobs, evaluate matches, and generate reports:

```sh
python main.py
```

- Job summaries will be saved to `results/ms-jobs.txt`.
- Best matching job URLs will be saved to `results/best-matches`.
- Detailed job descriptions will be saved as `results/<jobId>.txt`.
- Fit evaluations will be saved as Markdown files in `strong-matches/` and `other-matches/`.

## Customization

- **Target Locations:** Edit the `params["lc"]` list in [`main.py`](main.py) to change target cities.
- **Resume:** Update `sources/resume.txt` with your latest resume.
- **Job Filters:** Adjust the `params` dictionary in [`main.py`](main.py) for different job types or departments.

## Notes

- The script uses the Groq LLM API for job-resume matching. Ensure your API key is valid and you have sufficient quota.
- Only jobs with an 85%+ match are included in `best-matches`.
- Reports clearly call out missing qualifications and provide actionable recommendations.

## License

MIT License

---

**Author:** George Charon Ward  
**Contact:** gcward18@gmail.com
