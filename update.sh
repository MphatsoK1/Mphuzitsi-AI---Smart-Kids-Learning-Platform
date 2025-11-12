#!/bin/bash

# Set your GitHub username and password (replace with your actual credentials)
USERNAME="ben041"
PASSWORD="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"

# Change directory to your website directory on PythonAnywhere
cd /path/to/your/website/directory

# Configure Git to use the provided credentials
git config credential.helper 'store --file ~/.git-credentials'
echo "https://${USERNAME}:${PASSWORD}@github.com" > ~/.git-credentials

# Pull changes from the GitHub repository using the stored credentials
git pull origin main

# Restart your PythonAnywhere application if necessary
# This step depends on how you deploy your website on PythonAnywhere
# You may need to restart a WSGI server or any other application server you are using
# For example:
# touch /var/www/mywebsite_pythonanywhere_com_wsgi.py

echo "Website updated successfully!"