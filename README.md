# Steps to run locally in IDE.
1. Import the project.
2. In the terminal type the below command
   pip install -r requirements.txt
3. Click on the run button

Base URL: http://127.0.0.1:5000
The API only supports Pokemon with IDs between 1 and 50.
Errors are returned with appropriate HTTP status codes (400, 404, 500).
The /static/ endpoints serve images and may return 404 if the file is missing.

# Steps To run the project in local machine without IDE
1. Clone the project and go to GameMaster directory.
2. Create a Virtual Environment
   python -m venv venv
3. Activate the Virtual Environment
   Windows:
   venv\Scripts\activate
   macOS/Linux:
   source venv/bin/activate
4. Install Dependencies
   pip install -r requirements.txt
5. python main.py

# Swagger API Documentation 
After running the app on local, the swagger API documentation can be found at http://localhost:5000/api/docs


# Command to run unit tests:
python -m pytest

# Design Choices made by me
1. I am caching the images after they are fetched. We have a choice to either not cache images or to cache all the images in the beginning itself.

# Edge Cases
1. What if just before fetching the image, it gets deleted. AWS S3 is very reliable. 
However it is a design choice if we want to handle this scenario.

# Improvements
1. Improve unit testing
2. Improve logging
3. Improve documentation
4. Handle more edge cases and errors
5. Dockerize the project for deployment
6. Finalize deployment strategy and do the changes

# System Design

![image](https://github.com/user-attachments/assets/b5a11f94-6d6f-40e8-b960-2de6c0fdade8)
