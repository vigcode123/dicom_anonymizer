from pydicom import dcmread
from pathlib import Path
import argparse

IDENTIFIERS = []

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", help = "Target Path to Scans",required=True)
parser.add_argument("-ip", help = "Path to filename consisting of patient/surgeon identifying tags; text line spaced file", required= False)

args = parser.parse_args()

if args.ip:
    with open(args.ip, "r") as file:
        IDENTIFIERS.append(file.readline())
else:
    IDENTIFIERS=["Referring Physician's Name",
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


# print("What is the target directory?")
# target_dir = input()



def anonymous_callback(dataset, data_element):
    if data_element.name in IDENTIFIERS:
        if data_element.value != "" and data_element.value != None:
            raise Exception(str(data_element)+" ..... NOT SECURE")


target_dir = Path(args.path)
if not target_dir.exists():
    print("The target directory doesn't exist")
    raise SystemExit(1)

for entry in target_dir.iterdir():
    print(entry.name+" is valid file ..... ", end = "")
    try:
        fs = dcmread(str(target_dir)+"/"+entry.name)
    except Exception as e:
        print("x")
        raise Exception(e)
    print("GOOD")

    fs.walk(anonymous_callback)
    print("Identifiers not seen in "+entry.name)


print("ALL GOOD :)")

    
