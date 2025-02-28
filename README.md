# Steps to run locally in IDE.
1. Import the project.
2. In the terminal type the below command
   pip install -r requirements.txt
3. Click on the run button

# Command to run unit tests:
python -m pytest

# Edge Cases
1. What if just before fetching the image, it gets deleted. AWS S3 is very reliable. 
However it is a design choice if we want to handle this scenario.