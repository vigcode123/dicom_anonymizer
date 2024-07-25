# anonymizeScan.py
# This script anonymizes DICOM files by removing or modifying identifying information.

import argparse
from pathlib import Path
from tqdm import tqdm
import os
import dicom2nifti
import subprocess
from pydicom import dcmread

class AnonymizeScan():
    def __init__(self, target_dir:Path, print_value:str|None, remove_private_tags:bool, remove_curves:bool, identifier_path:None|str, niftipath:str|None) -> None:
        # Initialize the anonymizer with various options
        
        # Load identifiers from file or use default list
        if identifier_path:
            self.IDENTIFIERS = []
            with open(identifier_path, "r") as file:
                self.IDENTIFIERS.append(file.readline())
        else:
            # Default list of DICOM tags to anonymize
            self.IDENTIFIERS = ["Referring Physician's Name",
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

        # Check if target directory exists
        if not target_dir.exists():
            print("The target directory doesn't exist")
            raise SystemExit(1)
        
        # Load all DICOM files from the target directory
        self.fslst = []
        self.pathslst = []
        self.target_dir = target_dir
        for entry in target_dir.iterdir():
            path = str(self.target_dir)+"/"+entry.name
            self.pathslst.append(path)
            self.fslst.append(dcmread(path))
        
        # Set anonymization options
        self.remove_private_tags = remove_private_tags
        self.remove_curves = remove_curves
        self.print_value = print_value
        self.niftipath = niftipath
        self.identifier_path = identifier_path

        self.main()
    
    def person_names_callback(self, dataset, data_element):
        # Callback to anonymize person names in DICOM elements
        data_element_temp = data_element
        try:
            if data_element.name in self.IDENTIFIERS:
                data_element.value = ''
        except Exception as e:
            print("ERROR in "+str(data_element_temp)+": ", e)
            print("Reverting back to original fields..")
            if data_element_temp.name in self.IDENTIFIERS:
                data_element.value = data_element_temp.value
            print("Reverting Completed!")
            raise Exception(e)
    
    def curves_callback(self, dataset, data_element):
        # Callback to remove curve data from DICOM files
        if data_element.tag.group & 0xFF00 == 0x5000:
            del dataset[data_element.tag]

    def del_private_tags_callback(self, dataset, data_element):
        # Callback to remove private tags from DICOM files
        try:
            dataset.remove_private_tags()
        except Exception as e:
            print("Removal of Private Tags Failed. Error: "+str(e)+"Continuing ...")
    
    def print_dataset(self) -> None:
        # Print anonymized dataset to a file
        with open(self.print_value, "w+") as file:
            for i in range(len(self.fslst)):
                file.write("####################################\n"+self.pathslst[i]+"\n-----\n"+str(self.fslst[i])+"\n")
        print("Output saved to: ", self.print_value)
        
    def main(self) -> None:
        # Main anonymization process
        print("Starting program on the items in this folder("+str(self.target_dir)+") ...")

        # Confirm private tag removal if selected
        while self.remove_private_tags:
            print("Deleting the private tags is irreversible. Continue (y/n)?")
            cont = input()
            if (cont.lower() == "n"):
                exit()
            elif (cont.lower() == "y"):
                break

        # Process each DICOM file
        for i in tqdm(range(len(self.fslst))):
            fs = self.fslst[i]
            if self.remove_private_tags:
                fs.walk(self.del_private_tags_callback)
            
            fs.walk(self.person_names_callback)

            if self.remove_curves:
                fs.walk(self.curves_callback)

        print("Finished Anonymization. Saving changes ....")
        
        # Save anonymized DICOM files
        for i in tqdm(range(len(self.pathslst))):
            os.remove(self.pathslst[i])
            self.fslst[i].save_as(self.pathslst[i])
        
        # Print dataset if requested
        if self.print_value:
            self.print_dataset()
        else:
            print(self.fslst)
        
        # Convert to NIFTI if path provided
        if self.niftipath:
            try:
                print("###############################\n Finished. Converting to Nifti File Format ...")
                dicom2nifti.convert_directory(self.target_dir, self.niftipath, compression=True, reorient=True)
            except Exception as e:
                print("OOPS Error occurred. Take a look. :)")
                print(e)

if __name__ == "__main__":
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(
        prog = "Anonymizing CT/MRI Scans",
        description="Runs through DICOM Metadata and removes all identifying info on behalf of the patient or surgeon"
    )

    # Define command-line arguments
    parser.add_argument("-p", "--path", help="Target Path to Scans", required=True)
    parser.add_argument("--print", help="Filename to specifically print to", required=False)
    parser.add_argument("-rpt", help="Don't Remove Private Tags", action="store_false")
    parser.add_argument("-rc", help="Don't Remove Curves", action="store_false")
    parser.add_argument("-ip", help="Path to filename consisting of patient/surgeon identifying tags; text line spaced file", required=False)
    parser.add_argument("--niftipath", help="Path to output nifti files after conversion; not putting anything here will NOT convert", required=False)

    args = parser.parse_args()

    target_dir = Path(args.path)

    print("Checking contents ...")
    normal = True
    # Check if target is a directory of directories
    for entry in target_dir.iterdir():
        if entry.is_dir():
            print("Dir of Dirs detected. Switching to multiple MRI/CT Scans and auto check")
            normal = False
    
    if normal:
        #Run the checker for one directory
        print("All Good!")
        AnonymizeScan(target_dir, args.print, args.rpt, args.rc, args.ip, args.niftipath)
        print("FINISHED. CHECK STARTING NOW")
        if args.ip:
            subprocess.run(["python3", "checkScanAnonymity.py", "-p", target_dir.as_posix(), "-ip", args.ip])
        else:
            subprocess.run(["python3", "checkScanAnonymity.py", "-p", target_dir.as_posix()])
    else:
        #Run the checker for multiple directories
        for entry in target_dir.iterdir():
            if entry.is_dir():
                print("##########################################################\nMRI/CT Scan of "+entry.name+" starting now...")
                AnonymizeScan(entry, args.print, args.rpt, args.rc, args.ip, args.niftipath)
                print("FINISHED. CHECK STARTING NOW")
                if args.ip:
                    subprocess.run(["python3", "checkScanAnonymity.py", "-p", target_dir.as_posix(), "-ip", args.ip])
                else:
                    subprocess.run(["python3", "checkScanAnonymity.py", "-p", target_dir.as_posix()])