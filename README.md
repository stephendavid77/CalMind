# CalMind: Calendar Summarizer and Reporter

CalMind is a Python application designed to access your calendar events, summarize them using a Large Language Model (LLM), and then generate reports (HTML and Markdown) and send them via email. It supports multiple users, each with potentially multiple calendars (Google Calendar implemented, Apple Calendar as a placeholder).

## Features

*   **Calendar Integration:** Access events from Google Calendar (extensible to others).
*   **LLM Summarization:** Utilizes Google Gemini to summarize calendar events, highlighting key information and potential conflicts. Context for LLM summarization (e.g., for email summaries) can be provided in `calmind/llm/email_summary_context.md`.
*   **Report Generation:** Creates both HTML and Markdown reports of the summarized events.
*   **Email Delivery:** Sends the generated HTML report to specified recipients.
*   **Configurable:** Easily manage users, calendars, LLM settings, and email preferences via a `config.yaml` file.
*   **Dual Mode:** Can be run as a standalone command-line application or a simple web application.

## Getting Started

Follow these steps to set up and run CalMind on your local machine.

### Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)
*   A Google Account with access to Google Cloud Console and Google Gemini API.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/CalMind.git # Replace with your actual repository URL
cd CalMind
```

### 2. Install Dependencies

Dependencies will be automatically installed when you run the application using the provided `run.sh` script.

### 3. Configuration (`config.yaml`)

The application's behavior is controlled by the `config.yaml` file. A sample file, `config.yaml.sample`, is provided.

**DO NOT commit your `config.yaml` file to version control as it contains sensitive information.**

1.  **Create your `config.yaml`:**
    ```bash
    cp config.yaml.sample config.yaml
    ```
2.  **Edit `config.yaml`:** Open the `config.yaml` file in your text editor and fill in the details. The configuration is now validated using Pydantic models, so ensure the structure and data types are correct. Errors will be logged if validation fails.

    *   **`email_sender`:**
        *   `email`: Your sender email address (e.g., `your_email@example.com`).
        *   `password`: **IMPORTANT:** For Gmail, you'll need to generate an "App password" from your Google Account security settings. Do NOT use your regular Google password. For other providers, consult their documentation for app-specific passwords or SMTP details.
        *   `smtp_server`: Your email provider's SMTP server (e.g., `smtp.gmail.com`).
        *   `smtp_port`: Your email provider's SMTP port (e.g., `587` for TLS, `465` for SSL).

    *   **`llm: api_key`:**
        *   Obtain a Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
        *   Replace `"YOUR_GEMINI_API_KEY"` with your actual API key.

    *   **`users`:**
        *   Configure one or more users. Each user can have a `name`, `report_to_email`, and `days_to_fetch` (default is 30 days if not specified).
        *   **`calendars`:** Define the calendars for each user.

            *   **Google Calendar (`type: "google"`):**
                1.  **Enable Google Calendar API:** In your Google Cloud Project, go to **APIs & Services > Library** and enable the "Google Calendar API".
                2.  **Create OAuth 2.0 Client ID:** Go to **APIs & Services > Credentials**. Click **+ CREATE CREDENTIALS > OAuth client ID**. Select "Desktop app" as the application type. Give it a name and click "CREATE".
                3.  **Download `credentials.json`:** A dialog will appear with your client ID and client secret. Click "DOWNLOAD CLIENT CONFIGURATION" to get your `credentials.json` file.
                4.  **Place `credentials.json`:** Put this `credentials.json` file directly in your project's root directory (`CalMind/credentials.json`).
                5.  **Configure Redirect URIs:** In the Google Cloud Console, for the OAuth 2.0 Client ID you just created, go to its details page and add the following to "Authorized redirect URIs":
                    ```
                    http://localhost
                    http://127.0.0.1
                    ```
                    *   **Important:** If you encounter "Invalid Redirect: must contain a domain" error, ensure your OAuth client ID is indeed of type "Desktop app".
                6.  **Add Test Users:** If your OAuth consent screen is in "Testing" status, go to **APIs & Services > OAuth consent screen** and add the Google accounts you will use for authentication as "Test users".
                7.  **`calendar_ids` (Optional):** By default, it fetches from your "primary" calendar. To specify others, uncomment `calendar_ids` and list them (e.g., `calendar_ids: ["primary", "your_work_calendar_id@group.calendar.google.com"]`).

            *   **Apple iCloud Calendar (`type: "apple"`):**
                *   This is currently a placeholder. Full implementation would require using a CalDAV client or similar.
                *   For iCloud, you MUST use an app-specific password generated from your Apple ID account. See: [https://support.apple.com/en-us/HT204397](https://support.apple.com/en-us/HT204397)
                *   You can also specify `username`, `password`, and `url` directly in the `config.yaml` for Apple Calendar entries.

### 4. Run the Application

#### A. Standalone Application

Run the application from the project root directory using the provided script:

```bash
./run.sh
```

*   **First Run (Google Calendar):** The first time you run it for a Google Calendar, a web browser window will open asking you to authenticate with your Google account and grant permissions. Complete this process. A `token.json` file will be created in your project root to store authentication tokens for future runs.
*   **Output & Logging:** The application now uses Python's `logging` module for all output. You will see detailed logs in your console.
    *   `INFO` level messages provide general operational information.
    *   `WARNING` messages indicate recoverable issues or unusual states (e.g., LLM not configured).
    *   `ERROR` messages indicate non-recoverable issues.
    *   `DEBUG` messages (if logging level is set to DEBUG) provide detailed information, including masked API keys and full LLM prompts/responses.
*   **Reports Folder:** The `reports/` directory will be automatically cleared at the beginning of each application execution before new HTML and Markdown reports are generated.
*   **Email Delivery:** An email will be sent to the configured `report_to_email` address if email sender is properly set up.

#### B. Web Application (Flask)

Run the Flask web application from the project root directory:

```bash
python3 -m calmind.webapp
```

Then, open your web browser and navigate to `http://127.0.0.1:5000/`. You will see a simple interface to trigger reports for individual users or all users.

## Troubleshooting

*   **Configuration Validation Errors:** If you encounter errors related to `config.yaml` not being found or Pydantic validation failures, ensure:
    *   You are running the application from the project root directory using `python3 -m calmind.main`.
    *   Your `config.yaml` file is correctly formatted and all required fields are present and have valid data types as per the Pydantic models (e.g., valid email formats, correct integer types for ports). Check the detailed error messages in the logs for specific validation failures.
*   **`LLMClient Error: 404 models/gemini-pro is not found...` or `429 You exceeded your current quota...`:**
    *   **Model Not Found:** The model name might be incorrect or unavailable for your API key/region. Verify the correct model name (e.g., `gemini-1.5-pro-latest`) in `calmind/llm/client.py`.
    *   **Quota Exceeded:** You have hit your usage limits for the Gemini API. Wait for your quota to reset, or check your Google Cloud Project quotas and consider upgrading your plan if needed.
*   **`Error 400: redirect_uri_mismatch`:** Ensure `http://localhost` and `http://127.0.0.1` are correctly added to "Authorized redirect URIs" for your "Desktop app" OAuth 2.0 Client ID in Google Cloud Console.
*   **`Error 403: access_denied` (Google verification process):** Add your Google account as a "Test user" in the OAuth consent screen settings in Google Cloud Console.
*   **Authentication Failed (Apple Calendar):** Ensure you are using an [app-specific password](https://support.apple.com/en-us/HT204397) for your iCloud account in `config.yaml`, not your primary Apple ID password.
*   **Email Sending Failed (`nodename nor servname provided, or not known` or similar):** Verify your `smtp_server` and `smtp_port` settings in `config.yaml` are correct for your email provider. Also, ensure your `sender_email` and `sender_password` are accurate and that your email account allows third-party access or app passwords.

## Project Structure

```
CalMind/
├── calmind/
│   ├── __init__.py
│   ├── main.py             # Standalone application entry point
│   ├── webapp.py           # Web application entry point
│   ├── config.py           # Handles configuration loading
│   ├── calendars/
│   │   ├── __init__.py
│   │   ├── base.py         # Base Calendar class and CalendarEvent
│   │   ├── google_calendar.py # Google Calendar implementation
│   │   └── apple_calendar.py  # Apple Calendar placeholder
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py       # LLM (Gemini) client
│   │   └── summarizer.py   # LLM summarization logic
│   ├── reporting/
│   │   ├── __init__.py
│   │   └── generator.py    # Report generation (HTML, Markdown)
│   └── emailing/
│       ├── __init__.py
│       └── sender.py       # Email sending logic
├── templates/
│   └── index.html          # Web app HTML template
│   └── report_template.html # HTML report template
├── reports/                # Generated reports will be saved here (ignored by Git)
├── config.yaml.sample      # Sample configuration file
├── requirements.txt        # Python dependencies
└── .gitignore              # Specifies files to ignore in Git
```

## Contributing

Feel free to fork this repository, open issues, and submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details (if you choose to add one).
