# AI Housing Data Q&A Assistant

An AI-powered data Q&A tool that helps public-sector and nonprofit teams ask plain-English questions about housing datasets.

## Project Overview

Many housing departments, nonprofits, and civic organizations work with structured data but do not always have technical staff available to analyze it quickly.

This project demonstrates how AI can make data exploration easier for non-technical stakeholders by allowing users to upload a CSV file, view key metrics and charts, check dataset health, and ask plain-English questions about the data.

## Live Demo

Coming soon after deployment.

## Features

- Upload CSV housing datasets
- Preview uploaded data
- View key metrics such as total cases, top ZIP code, top eviction cause, and highest month
- Display visual charts by month, ZIP code, and eviction cause
- Run a basic dataset health check
- Ask plain-English questions about the dataset
- Use Claude API for live AI responses
- Includes demo fallback mode when API credits are unavailable
- Download generated answers as text
- Maintain Q&A history during the session

## Tech Stack

- Python
- Streamlit
- Pandas
- Anthropic Claude API
- python-dotenv
- Git & GitHub

## Example Questions

Users can ask questions such as:

- Which ZIP codes have the highest eviction activity?
- What is the most common eviction cause?
- Summarize trends by month.
- Which areas may need additional support?
- What patterns should housing managers monitor?
- What risks do you see in this dataset?
- What recommendations would you make?
- Explain the findings for non-technical stakeholders.

## Sample Dataset

The repository includes a sample housing dataset with 32 records across multiple ZIP codes, eviction causes, and months.

The sample data is designed to demonstrate:

- Repeated eviction activity by ZIP code
- Rent-related eviction patterns
- Monthly case trends
- Common eviction causes
- Public-sector reporting use cases

## Repository Structure

```text
ai-housing-data-qa-assistant/

├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── sample_data/
│   └── sample_housing_data.csv
│
└── screenshots/