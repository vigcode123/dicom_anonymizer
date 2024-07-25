# checkScanAnonymity.py
# This script checks DICOM files for any remaining identifying information after anonymization.

from pydicom import dcmread
from pathlib import Path
import argparse

# List to store identifiers (DICOM tags) to check
IDENTIFIERS = []

# Set up command-line argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", help="Target Path to Scans", required=True)
parser.add_argument("-ip", help="Path to filename consisting of patient/surgeon identifying tags; text line spaced file", required=False)

args = parser.parse_args()

# Load identifiers from file if provided, otherwise use default list
if args.ip:
    with open(args.ip, "r") as file:
        IDENTIFIERS.append(file.readline())
else:
    IDENTIFIERS = ["Referring Physician's Name",
                   "Performing Physician's Name",
                   "Name of Physician(s) Reading Study",
                   "Operators' Name",
                   "Patient's Name ",
                   "Patient's Birth Date",
                   "Patient's Sex",
                   "Patient's Age",
                   "Additional Patient History",
                   "Patient's Size",
                   "Patient's Weight"]

def anonymous_callback(dataset, data_element):
    # Callback function to check if a DICOM element contains identifying information
    if data_element.name in IDENTIFIERS:
        if data_element.value != "" and data_element.value is not None:
            raise Exception(str(data_element)+" ..... NOT SECURE")

# Get the target directory from command-line arguments
target_dir = Path(args.path)
if not target_dir.exists():
    print("The target directory doesn't exist")
    raise SystemExit(1)

# Iterate through all files in the target directory
for entry in target_dir.iterdir():
    print(entry.name+" is valid file ..... ", end="")
    try:
        # Try to read the file as a DICOM file
        fs = dcmread(str(target_dir)+"/"+entry.name)
    except Exception as e:
        print("x")
        raise Exception(e)
    print("GOOD")

    # Walk through the DICOM dataset and check for identifying information
    fs.walk(anonymous_callback)
    print("Identifiers not seen in "+entry.name)

# If no exceptions were raised, all files are properly anonymized
print("ALL GOOD :)")