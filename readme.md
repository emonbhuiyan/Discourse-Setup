# Discourse Automation Tool

The **Discourse Automation Tool** is a powerful and user-friendly web application designed to automate the management of Discourse forums. With this tool, you can easily configure your forum, create categories, bulk-post topics, and manage site settings—all from a centralized dashboard.

## Features

- **User-Friendly Dashboard**: A clean and intuitive interface to manage all automation tasks.
- **Category Management**: Create and update categories with descriptions and custom settings.
- **Bulk Topic Posting**: Automate the creation of multiple topics in specific categories.
- **Google OAuth Integration**: Configure Google login for your Discourse forum.
- **Customizable Color Schemes**: Apply custom color schemes to your forum themes.
- **Execution History**: View logs of all executed scripts, including timestamps and statuses.
- **Real-Time Script Execution**: Monitor script execution in real-time with live output streaming.
- **Responsive Design**: Fully responsive UI built with Bootstrap for seamless use on any device.

## Installation

Follow these steps to set up and run the project:

### Prerequisites

- Python 3.12 or higher
- Discourse forum with admin access
- API Key and Admin Username for your Discourse instance

### Steps

1. Install Python virtual environment:
   ```bash
   $ apt install python3.12-venv
   ```
2. Create and activate a virtual environment:
    ```bash
    $ python3 -m venv venv
    $ source venv/bin/activate
    ```
3. Install dependencies:
    ```bash
    $ pip install -r requirements.txt
    ```
4. Run the application:
    ```bash
    $ python3 app.py
    ```
5. Deactivate the virtual environment when done:
    ```bash
    $ deactivate
    ```
### Deployment
To deploy the application using Gunicorn:

1. Navigate to the project directory:
    ```bash
    cd ~/discourseSetup
    ```
2. Start the application with Gunicorn:
    ```bash
    gunicorn --bind 127.0.0.1:5000 app:app
    ```
3. For background execution:
    ```bash
    nohup gunicorn --bind 0.0.0.0:5000 app:app > nohup.log 2>&1 &
    ```
## Configuration
### Environment Variables
Create a `.env` file in the project root with the following variables:
    ```
    WEBAPP_ADMIN_USERNAME=admin
    WEBAPP_ADMIN_PASSWORD=admin
    SECRET_KEY=yoursecretkey
    ```
### Application Configuration
The application uses a `config.py` file to store settings. You can configure the following:

- **Occupation**: The occupation or purpose of the forum.
- **API Key**: Your Discourse API key.
- **Admin Username**: The admin username for API requests.
- **Categories**: A dictionary of categories and their descriptions.
- **Topics**: A list of topics to be created in bulk.
- **Google OAuth**: Client ID and secret for Google login.
- **GTM ID**: Google Tag Manager ID.
The configuration can be updated via the **Configure** page in the web app.
## Usage
### Dashboard
The dashboard provides an overview of the tool's features, including:

- **Run Scripts**: Execute automation scripts for setup, category creation, and bulk posting.
- **Execution History**: View logs of previously executed scripts.

### Scripts
- **Setup Script**: Configures site settings, Google OAuth, and other Discourse options.
- **Category Script**: Creates and updates categories with descriptions.
- **Bulk Post Script**: Automates the creation of topics in specified categories.

### Real-Time Output
Monitor the progress of script execution in real-time through the **Run Script** page.

## File Structure
```bash
.
├── [app.py]                 # Main application file
├── [bulk_post.py]           # Script for bulk posting topics
├── [category.py]            # Script for category management
├── [config.py]              # Configuration file
├── [database.py]            # Database for execution history
├── [setup.py]               # Script for initial setup
├── [setup_debug.py]         # Debugging utilities
├── templates/               # HTML templates for the web app
├── static/                  # Static files (CSS, JS)
├── [requirements.txt]       # Python dependencies
└── .env                     # Environment variables
```

## Technologies Used
- **Backend**: Flask (Python)
- **Frontend**: Bootstrap, JavaScript
- **Database**: SQLite
- **API Integration**: Discourse API

## Contributing
Contributions are welcome! Feel free to fork the repository and submit a pull request.

## License
This project is licensed under the [MIT License](LICENSE). See the LICENSE file for details.