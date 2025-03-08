
# Birthday Reminder

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](LICENSE)

**Birthday Reminder** is a secure, web-based application built with Streamlit that integrates Google OAuth for authentication and a MySQL database for data storage. It features robust security measures, including SSL-encrypted database connections, Fernet encryption to protect sensitive birthday data, and innovative use of Gemini AI for personalized message generation.


---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Database & Data Encryption](#database--data-encryption)
- [Deployment](#deployment)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## About

**Birthday Reminder** is designed to help you manage and celebrate birthdays securely and efficiently. Built with Streamlit, the application leverages Google OAuth for secure user authentication and uses a MySQL database for storing authorized user emails. Sensitive birthday data is encrypted using Fernet to ensure maximum confidentiality and integrity. The app also utilizes Gemini AI to generate personalized birthday messages, and provides an option to email dashboard responses to users.


---


## Features

- **Secure Authentication:** Log in with your Google account via OAuth.
- **MySQL Integration:** Store and manage birthday and user data in a secure MySQL database.
- **Data Encryption:** Encrypt sensitive birthday data using Fernet encryption.
- **Dynamic Dashboard:** View today’s birthdays in an intuitive, responsive interface.
- **Admin Panel:** Manage authorized users directly from the dashboard.
- **Enhanced UI/UX:** Custom CSS styles deliver a professional and engaging experience.
- **Email Notification:** Users have the option to receive a copy of their dashboard responses via email.
- **Gemini AI Integration:** Generate personalized birthday messages using Gemini AI.

---

## Technologies

- **Python:** Primary programming language.
- **Streamlit:** Framework for building interactive web applications.
- **Google OAuth:** For secure user authentication.
- **MySQL:** Database system for storing application data.
- **MySQL Connector/Python:** For MySQL integration.
- **Cryptography (Fernet):** For data encryption.
- **Pandas:** For data manipulation and analysis.
- **python-dotenv:** For managing environment variables.

---

## Installation

### Prerequisites

- Python 3.7 or later.
- MySQL database (with SSL support).
- A Google account for OAuth authentication.
- Git (for cloning the repository).

### Steps

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/Hariesh28/Birthday-Reminder.git
    cd Birthday-Reminder
    ```

2. **Set Up a Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies:**

    A `requirements.txt` file is provided:

    ```bash
    pip install -r requirements.txt
    ```

---

## Configuration

### Google OAuth Setup

1. Visit the [Google Developers Console](https://console.developers.google.com/).
2. Create a new project and enable the OAuth 2.0 API.
3. Configure the OAuth consent screen and create OAuth credentials.
4. Download the credentials file and update your environment variables:
    - `CLIENT_ID`
    - `CLIENT_SECRET`
    - `REDIRECT_URI`

### MySQL Database Setup

Configure your MySQL database and ensure the following environment variables are set (typically in a `.env` file):

- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`
- `AIVEN_CA_PEM` (SSL CA certificate content)

### Application Settings

- `ADMIN_EMAIL` – Administrator email address.
- `KEY` – Fernet encryption key (generate using `encryption.py` if needed).
- `API` – API key for Gemini AI.

---

## Usage

To run the application locally, execute:

```bash
streamlit run app.py
```

The application will launch in your default web browser. Log in with your Google account to access your personalized dashboard displaying today’s birthdays.

After logging in, you can now click the "Email me a copy" button to receive an email copy of your dashboard responses.
Gemini AI is used within the app to generate personalized birthday messages.

### Troubleshooting

- Verify that your environment variables (especially for Google OAuth and MySQL) are correctly set.
- Ensure the SSL certificate content is provided via `AIVEN_CA_PEM` for secure MySQL connections.
- Check that all dependencies are properly installed and compatible with your Python version.

---

## Database & Data Encryption

**MySQL Database:**
All application data, including authorized user emails, is stored in a MySQL database. Secure SSL connections (using the `AIVEN_CA_PEM` certificate) ensure data integrity and privacy.

**Data Encryption:**
Sensitive birthday data is encrypted using Fernet before being stored in the database. Use the provided `encryption.py` script to encrypt data and generate a secure key (`secret.key`), which is then used for encryption and decryption.

---

## Deployment

The application is deployed at [Birthday Reminder App](https://birthday-reminder-qn9e.onrender.com) on Render, while the MySQL database is hosted on [Aiven](https://aiven.io) for secure and reliable data management. Ensure that all environment variables are securely managed in your deployment environment. Containerization with Docker is also recommended for consistent deployments.

---

## File Structure

```
Birthday-Reminder/
│
├── app.py                      # Main Streamlit application with Google OAuth, MySQL integration, and Gemini AI usage
├── birthday.py                 # Logic for fetching and displaying birthday data from CSV
├── birthday_email_notifier.py  # Module for sending dashboard responses via email
├── encryption.py               # Script to encrypt sensitive birthday data
├── secret.key                  # File containing the Fernet encryption key
├── .env                        # Environment variables file (not included in repository)
└── README.md                   # Project documentation

```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository.**
2. **Create a New Branch:**

    ```bash
    git checkout -b feature/your-feature-name
    ```

3. **Commit Your Changes:**

    ```bash
    git commit -m "Description of changes"
    ```

4. **Push to Your Branch:**

    ```bash
    git push origin feature/your-feature-name
    ```

5. **Open a Pull Request:** Provide a detailed description of your changes and reference any related issues.

---

## License

This project is licensed under the **GPL-3.0 License**. See the [LICENSE](LICENSE) file for details.

---

## Contact

For questions or feedback, please open an issue on this repository or contact the maintainer directly:

- **Hariesh28** - [GitHub Profile](https://github.com/Hariesh28)
