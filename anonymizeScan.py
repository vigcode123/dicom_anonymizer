from pydicom import dcmread
import argparse
from pathlib import Path
from tqdm import tqdm
import os
import dicom2nifti
import subprocess

class AnonymizeScan():
    def __init__(self, target_dir:Path, print_value:str|None,remove_private_tags:bool, remove_curves:bool, identifier_path:None|str, niftipath:str|None) -> None:

        if identifier_path:
            self.IDENTIFIERS = []
            with open(identifier_path, "r") as file:
                self.IDENTIFIERS.append(file.readline())
        else:
            self.IDENTIFIERS=["Referring Physician's Name",
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

        if not target_dir.exists():
            print("The target directory doesn't exist")
            raise SystemExit(1)
        
        self.fslst = []
        self.pathslst = []
        self.target_dir = target_dir
        for entry in target_dir.iterdir():
            # print(entry.name)
            path = str(self.target_dir)+"/"+entry.name
            self.pathslst.append(path)
            self.fslst.append(dcmread(path))
        
        self.remove_private_tags = remove_private_tags
        self.remove_curves = remove_curves
        self.print_value = print_value

        if niftipath:
            self.niftipath = niftipath
        else:
            self.niftipath = None
        
        if identifier_path:
            self.identifier_path = identifier_path
        else:
            self.identifier_path = None

        self.main()
    
    def person_names_callback(self,dataset, data_element):
        data_element_temp = data_element
        try:
            if data_element.name in self.IDENTIFIERS:
                data_element.value = ''
        except Exception as e:
            print("ERROR in "+str(data_element_temp)+": ",e)
            print("Reverting back to original fields..")
            if data_element_temp.name in self.IDENTIFIERS:
                data_element.value = data_element_temp.value

            print("Reverting Completed!")
            raise Exception(e)
    

    def curves_callback(self,dataset, data_element):
        if data_element.tag.group & 0xFF00 == 0x5000:
            del dataset[data_element.tag]

    def del_private_tags_callback(self,dataset,data_element):
        try:
            dataset.remove_private_tags()
        except Exception as e:
            print("Removal of Private Tags Failed. Error: "+e+"Continuing ...")
    
    def print_dataset(self) -> None:
        with open(self.print_value,"w+") as file:
            for i in range(len(self.fslst)):
                file.write("####################################\n"+self.pathslst[i]+"\n-----\n"+str(self.fslst[i])+"\n")
        print("Output saved to: ",self.print_value)
        
    def main(self) -> None:
        print("Starting program on the items in this folder("+str(self.target_dir)+") ...")

        while self.remove_private_tags:
            print("Deleting the private tags is irreverisble. Continue (y/n)?")
            cont = input()
            if (cont.lower() == "n"):
                exit()
            elif (cont.lower() == "y"):
                break

        for i in tqdm(range(len(self.fslst))):
            fs = self.fslst[i]
            if self.remove_private_tags:
                fs.walk(self.del_private_tags_callback)
            
            fs.walk(self.person_names_callback)

            if (self.curves_callback):
                fs.walk(self.curves_callback)
        print("Finished Anonymization. Saving changes ....")
        for i in tqdm(range(len(self.pathslst))):
            os.remove(self.pathslst[i])
            self.fslst[i].save_as(self.pathslst[i])
        
        if self.print_value:
            self.print_dataset()
        else:
            print(self.fslst)
        
        if self.niftipath:
            try:
                print("###############################\n Finished. Converting to Nifti File Format ...")
                dicom2nifti.convert_directory(self.target_dir, self.niftipath, compression=True, reorient=True)
            except Exception as e:
                print("OOPS Error occured. Take a look. :)")
                print(e)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = "Anonymizing CT/MRI Scans",
        description="Runs through DICOM Metadata and removes all identifying info on behalf of the patient or surgeon"
    )

    #TODO:remove_private_tags:bool, remove_anonymous_codes:bool, remove_curves:bool, identifier_path:None|str
    #           store false              store true                      store false        nothing
    parser.add_argument("-p", "--path", help = "Target Path to Scans",required=True)
    parser.add_argument("--print", help = "Filename to specifically print to", required= False)
    parser.add_argument("-rpt", help="Don't Remove Private Tags", action = "store_false")
    parser.add_argument("-rc", help="Don't Remove Curves", action = "store_false")
    parser.add_argument("-ip", help = "Path to filename consisting of patient/surgeon identifying tags; text line spaced file", required= False)
    parser.add_argument("--niftipath", help = "Path to output nifti files after conversion; not putting anything here will NOT convert",required = False)

    args = parser.parse_args()

    target_dir = Path(args.path)

    print("Checking contents ...")
    normal = True
    for entry in target_dir.iterdir():
        if entry.is_dir():
            print("Dir of Dirs detected. Switching to multiple MRI/CT Scans and auto check")
            normal = False
    
    if normal:
        print("All Good!")
        AnonymizeScan(target_dir, args.print, args.rpt,args.rc,args.ip, args.niftipath)
        print("FINISHED. CHECK STARTING NOW")
        if args.ip:
            subprocess.run(["python3", "checkScanAnonymity.py","-p",target_dir.as_posix(), "-ip",args.ip])
        else:
            subprocess.run(["python3", "checkScanAnonymity.py","-p",target_dir.as_posix()])

    else:
        for entry in target_dir.iterdir():
            if entry.is_dir():
                print("##########################################################\nMRI/CT Scan of "+entry.name+" starting now...")
                AnonymizeScan(entry, args.print, args.rpt,args.rc,args.ip, args.niftipath)
                print("FINISHED. CHECK STARTING NOW")
                if args.ip:
                    subprocess.run(["python3", "checkScanAnonymity.py","-p",target_dir.as_posix(), "-ip",args.ip])
                else:
                    subprocess.run(["python3", "checkScanAnonymity.py","-p",target_dir.as_posix()])

