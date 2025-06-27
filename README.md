# 📚 FK-WEB-CRAWLER: 
### A Web Crawler project with Change Detection, Scheduler, REST API Features

A fully-featured Python-based data pipeline that:
- Crawls book data from `books.toscrape.com`
- Detects changes using fingerprinting
- Stores books in MongoDB Atlas
- Logs changes and inserts
- Schedules daily updates
- Serves data through a FastAPI-secured RESTful API with rate limiting and authentication

---

## 📁 Project Structure

```
FK-CRAWLER/
│
├── api/                            # FastAPI server
│   ├── auth/                       # API Key Auth
│   |   ├── security.py             # Authentication
│   ├── models/                     # Pydantic schemas
│   |   ├── book.py                 # Pydantic model for Books
│   |   ├── change.py               # Pydantic model for Logs
│   |   ├── schemas.py              # Serialization functions for book and logs
│   ├── routes/                     # API endpoints
│   |   ├── __init__.py             # 
│   |   ├── books.py                # 
│   |   ├── changes.py              # 
│   ├── __init__.py                 # 
│   ├── main_test.py                # 
│   └── main.py                     # 
│
├── crawler/                        # Web scraping logic
│   ├── fkcrawling/
│   |   ├── spiders/                # Scrapy spiders
│   |   |   ├── __init__.py         # 
│   |   |   ├── book_schema.py      #
│   |   |   ├── crawling_spider.py  # 
│   |   |   └── mongodb_client.py   #
│   |   ├── __init__.py             #
│   |   ├── items.py                # 
│   |   ├── middlewares.py          # MongoDB insertion logic
│   |   ├── pipelines.py            # MongoDB insertion logic
│   |   ├── settings.py             # Scrapy config
│   └── └── logs/
│           └── activity.log        #
│ 
├── scheduler/                      # Daily job scheduler
│   ├── daily_scheduler.py
│   └── crawler_runner.py
│
├── utilities/                      # Helper utilities
│   ├── reports/
│   |   ├── report.json             #
│   ├── db_config.py                # MongoDB client
│   ├── generate_report.py          # Daily change report
│   └── log_config.py               # Log setup
│
├── tests/                          # Unit & integration tests (TBD)
│
├── logs/                           # Logging output
│   ├── activity.log
│
├── reports/                        # Daily JSON/CSV reports
│
├── .env                            # Secure API_KEY and DB URI
├── .gitignore
├── requirements.txt
├── README.md                       # This file
└── scrapy.cfg
```

---

## 🚀 Features

- ✅ Scrapy-powered web crawler
- ✅ MongoDB Atlas integration with deduplication
- ✅ Fingerprint-based change detection
- ✅ Change logging and raw HTML snapshot
- ✅ APScheduler-powered daily job
- ✅ Daily change reports in JSON and CSV
- ✅ RESTful FastAPI server:
  - `/books` with filtering, pagination, sorting
  - `/books/{book_id}` for book details
  - `/changes` to get recent logs
- ✅ API Key Authentication
- ✅ Rate limiting (100 req/hr per IP)
- ✅ OpenAPI (Swagger) docs

---

## 🔧 Setup Instructions

### 📦 Requirements

- Python 3.10+
- MongoDB Atlas account
- pipenv / virtualenv (recommended)

### 📁 1. Clone the Repository

```bash
git clone https://github.com/yourusername/fk-crawler.git
cd fk-crawler
```

### 📁 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### ⚙️ 3. Create `.env` File

Create a `.env` file at the root:

```
MONGODB_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/
API_KEY=123456
```

> ✅ `.env` is automatically loaded using `dotenv`.

---

## 🕷️ Run Crawler

```bash
cd crawler/fkcrawling
scrapy crawl fkcrawler
```

- Inserts books
- Logs changes (if any)
- Stores raw HTML
- Logs output to `/logs/activity.log`

---

## 🗓️ Run Scheduler

```bash
cd scheduler
python daily_scheduler.py
```

- Crawls every day using APScheduler
- Detects new books or changes
- Logs them in MongoDB and filesystem

---

## 🧪 Run FastAPI Server

```bash
cd api
uvicorn main:app --reload
```

- API is hosted at `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

---

## 🔐 API Key Usage

All endpoints are protected via API key.

### Headers:

```
FKCRAWLER-API-KEY: 123456
```

---

## 📂 API Endpoints

| Endpoint          | Method | Description                              |
|------------------|--------|------------------------------------------|
| `/books`         | GET    | Get all books (filter, sort, paginate)   |
| `/books/{id}`    | GET    | Get book by MongoDB ObjectId             |
| `/changes`       | GET    | Get recent changes                       |
| `/docs`          | GET    | Swagger UI (OpenAPI spec)                |

---

## 📤 Daily Report Output

On successful run, you'll get:

```bash
/reports/
├── change_report_YYYY-MM-DD.json
├── change_report_YYYY-MM-DD.csv
```

Includes:
- New insertions
- Fields changed
- Source URLs and timestamps

---

## 🧪 Testing

Unit and integration tests will be added in `/tests/`.

Planned with `pytest`, `mongomock`, and `httpx` for:
- API endpoints
- DB operations
- Crawling output
- Scheduler jobs

---

## 💡 Sample MongoDB Document

```json
{
  "_id": ObjectId("123..."),
  "name": "A Light in the Attic",
  "price_with_tax": 12.99,
  "availability": "In stock",
  "rating": 3,
  "source_url": "https://books.toscrape.com/catalogue/.../index.html",
  "raw_html": "<html>...</html>",
  "fingerprint": "abc123...",
  "crawl_timestamp": "2025-06-27T10:00:00Z"
}
```

---

## 🧾 Deliverables Checklist (from PDF ✅)

| Requirement                               | Status     |
|------------------------------------------|------------|
| ✅ Crawler using Scrapy                  | Done       |
| ✅ Scheduler with change detection       | Done       |
| ✅ Change log storage                    | Done       |
| ✅ FastAPI server                        | Done       |
| ✅ API key + rate limiting               | Done       |
| ✅ Swagger UI                            | Done       |
| ✅ `.env` support                        | Done       |
| ✅ Daily reports (JSON + CSV)            | Done       |
| ✅ Screenshot/logs of scheduler/crawler  | ✔️ See `/logs` |
| ✅ Folder structure & README             | ✅ This file |

---

## 📬 Postman / Swagger UI

Use [http://localhost:8000/docs](http://localhost:8000/docs) to interactively test all endpoints.

Or import a Postman collection (see repo if added).

---

## 🧠 Future Improvements

- Add unit + integration tests
- Dockerize for consistent environments
- Add email alerts for major changes
- Add export formats: PDF, Excel

---

## 🧑‍💻 Author

**Sadman Alvee**  
📧 alvee@example.com  
🔗 [GitHub](https://github.com/sadmanalvee)

---

## 📄 License

MIT License – feel free to use, improve, and contribute!
