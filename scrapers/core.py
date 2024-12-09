import datetime
from typing import List
import pickle
import os
import requests
import PyPDF2
import io
import numpy as np
import pytesseract
import re
import cv2
from pdf2image import convert_from_bytes


class AuthorInfo:
    def __init__(self, name: str, surname: str, eai_url: str):
         self.name = name
         self.surname = surname
         self.eai_url = eai_url
         self.full_name = f"{self.name} {self.surname}"
         self.link = ""
         self.pdf_link = ""
         self.publication_date = datetime.datetime.now()
         self.source = ""
         self.title = ""
         self.eai_match = False
         self.affiliation = ""
         self.venue = ""

    def __init__(self, full_name:str, eai_url: str):
        self.full_name = full_name
        self.eai_url = eai_url
        self.link = ""
        self.pdf_link = ""
        self.publication_date = None
        self.data_source = ""
        self.publication = ""
        self.title = ""
        self.eai_match = False
        self.affiliation = ""
        self.type = ""
        self.citations= 0

    def __str__(self):
        s = ""
        s += f"{self.full_name}, "
        s += f"{self.eai_url}, "
        s += f"{self.link}, "
        s += f"{self.pdf_link}, "
        s += f"{self.publication_date}, "
        s += f"{self.data_source}, "
        s += f"{self.publication}, "
        s += f"{self.title}, "
        s += f"{self.eai_match}, "
        s += f"{self.affiliation},"
        if self.affiliation is not None:
            s += f"{self.affiliation},"
        else:
            s += ","
        s += f"{self.type},"
        s += f"{self.citations}"
        return s

    def to_string(self):
        s = ""
        s += f"{self.full_name}\t"
        s += f"{self.eai_url}\t"
        s += f"{self.link}\t"
        s += f"{self.pdf_link}\t"
        s += f"{self.publication_date}\t"
        s += f"{self.data_source}\t"
        s += f"{self.publication}\t"
        s += f"{self.title}\t"
        s += f"{self.eai_match}\t"
        if self.affiliation is not None:
            s += f"{self.affiliation}\t"
        else:
            s += "\t"
        s += f"{self.type}\t"
        s += f"{self.citations}"
        return s


def serialize(data: List[AuthorInfo], output_file_name: str):
    with open(output_file_name, 'wb') as file:
            pickle.dump(data, file)

def deserialize(input_file_name: str):
    deserialized_obj = None
    with open(filename, 'rb') as file:
        deserialized_obj = pickle.load(file)
    return deserialized_obj

def create_folder_if_not_exists(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def validate_affiliation(pdf_url_path: str, affiliation: str):
    response = requests.get(pdf_url_path)
    if response.status_code == 200:
        pdf_file = io.BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        page = reader.pages[0]
        text = page.extract_text()
        if affiliation.upper() in text.upper():
            return True
    return False

import numpy as np
import cv2
import requests
from io import BytesIO
import pytesseract
from pdf2image import convert_from_bytes
#from google.colab.patches import cv2_imshow

# Function to download PDF from URL
def download_pdf_from_url(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to download PDF from {pdf_url}")
        return None

# Function to extract document layout
def extract_layout(image):
    # Convert the image to grayscale
    pdf_content = download_pdf_from_url(pdf_url)

    images = convert_from_bytes(pdf_content)

    # Process only the first page (first image)
    first_page_image = np.array(images[0])

    # Resize the image to make it bigger
    resized_image = cv2.resize(first_page_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Perform edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Find contours in the edge-detected image
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours on the original image
    layout = image.copy()
    cv2.drawContours(layout, contours, -1, (0, 255, 0), 2)

    return layout

# Function to perform OCR on document
def perform_ocr(image):
    # Perform OCR using Tesseract
    ocr_text = pytesseract.image_to_string(image)
    return ocr_text

# ArXiv PDF URL
def url_to_layout(url):
    
    # Download PDF from ArXiv URL
    pdf_content = download_pdf_from_url(url)

    # Convert PDF to images
    images = convert_from_bytes(pdf_content)

    # Process only the first page (first image)
    first_page_image = np.array(images[0])

    # Resize the image to make it bigger
    resized_image = cv2.resize(first_page_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Extract layout from the resized image
    layout_image = extract_layout(resized_image)

    # Perform OCR on the resized image
    ocr_text = perform_ocr(resized_image)
    cv2.imshow('',layout_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return layout_image, ocr_text

# Display the layout image


# Print OCR text for the first page
#print("OCR Text - First Page:")
#print(ocr_text)


import re

def perform_query(text, query):
    # Compile the regular expression pattern for the query
    pattern = re.compile(query, re.IGNORECASE)

    # Search for the pattern in the text
    matches = pattern.finditer(text)

    # Store the results
    results = []

    # Iterate over the matches
    for match in matches:
        # Get the start index of the match
        match_start = match.start()

        # Get the next two strings after the match index
        next_strings = text[match_start:].split(maxsplit=4)[1:4]

        # Append the match and next two strings to the results
        results.append((match.group(), *next_strings))

    # Return the results
    return results

#ocr_text = url_to_layout("https://arxiv.org/pdf/2305.00380v1.pdf")
#results = perform_query(ocr_text, "Jennifer")


#print(results)

#print(validate_affiliation("https://arxiv.org/pdf/2305.00380v1.pdf", "NORTHEASTERN UNIVERSITY"))
#rint(validate_affiliation("https://arxiv.org/pdf/2311.00858.pdf", "NORTHEASTERN UNIVERSITY"))
#print(process_pdf("https://arxiv.org/pdf/2311.00858.pdf","Jennifer Dy"))

