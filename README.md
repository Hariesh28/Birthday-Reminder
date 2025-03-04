# Birthday Reminder

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](LICENSE)

Birthday Reminder is a **Streamlit-based web application** that allows users to log in using Google OAuth and view a list of upcoming birthdays. Only authorized users can access the dashboard, ensuring privacy and security.

## Table of Contents
- [About](#about)
- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Deployment](#deployment)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## About
Birthday Reminder is designed to help you keep track of important birthdays in a secure and interactive way. Built with Streamlit, this application leverages Google OAuth for secure authentication, ensuring that only authorized users can access sensitive birthday data. The application also includes encryption for data storage, protecting your information.

## Features
- **Secure Authentication:** Log in with your Google account using OAuth.
- **Dashboard View:** Easily view a list of upcoming birthdays.
- **Data Protection:** Birthday data is encrypted before storage.
- **User-Friendly Interface:** Built with Streamlit for a seamless interactive experience.

## Technologies
- **Python:** The main programming language.
- **Streamlit:** For creating the web application interface.
- **Google OAuth:** To enable secure login.
- **Encryption Modules:** For protecting sensitive data.
- **JSON & CSV:** For data storage and management.

## Installation

### Prerequisites
- Python 3.7 or later
- A Google account for OAuth authentication

### Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Hariesh28/Birthday-Reminder.git
   cd Birthday-Reminder
   ```
2. **Set up a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate   # For Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   If a `requirements.txt` file is provided:
   ```bash
   pip install -r requirements.txt
   ```
   Otherwise, install the necessary packages manually:
   ```bash
   pip install streamlit google-auth google-auth-oauthlib
   ```

## Configuration

### Google OAuth Setup
1. Navigate to the [Google Developers Console](https://console.developers.google.com/).
2. Create a new project and enable the OAuth 2.0 API.
3. Configure the OAuth consent screen and create OAuth credentials.
4. Download the `credentials.json` file and place it in the project root directory.
5. Update the app configuration as necessary (for example, by specifying allowed domains).

### Data Encryption
- The application uses `encryption.py` to encrypt birthday data, which is stored in `data-encrypted.csv`. Make sure to set up your encryption keys or any other configuration as needed.

## Usage
To run the application locally, execute the following command:
```bash
streamlit run app.py
```
Once running, the app will launch in your default web browser. You will be prompted to log in with your Google account. After authentication, you can access the dashboard and view the upcoming birthdays.

## Deployment
The application is deployed and can be accessed here: [Birthday Reminder App](https://birthday-reminder.streamlit.app/)

## File Structure
```
Birthday-Reminder/
│
├── app.py             # Main Streamlit application
├── birthday.py        # Handles birthday data and related logic
├── encryption.py      # Encryption and decryption utilities
├── data.json          # JSON file for storing birthday information
├── data-encrypted.csv # Encrypted CSV file containing birthday records
├── LICENSE            # Project license (GPL-3.0)
└── README.md          # Project documentation
```

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add some feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request with a clear description of your changes.

Please follow the existing coding standards and include tests when applicable.

## License
This project is licensed under the **GPL-3.0 License**. See the [LICENSE](LICENSE) file for details.

## Contact
For questions or feedback, please open an issue on this repository or contact the maintainer directly:
- **Hariesh28** - [GitHub Profile](https://github.com/Hariesh28)
