# DICOM Anonymizer

This Python script anonymizes DICOM (Digital Imaging and Communications in Medicine) files by removing or modifying identifying information. It's designed to process both individual DICOM files and directories containing multiple DICOM files.

## Prerequisites

Before running the script, ensure you have the following installed:

- Python 3.x
- Required Python packages:
  - pydicom
  - tqdm
  - dicom2nifti
  - etc. that are enumerated in the requirements.txt

You can install these packages using pip:

```
pip install -r requirements.txt
```

## Usage

To run the script, use the following command:

```
python anonymizeScans.py -p <path_to_dicom_files> [options]
```

### Required Arguments

- `-p, --path`: Path to the directory containing DICOM files or directories of DICOM files.

### Optional Arguments

- `--print <filename>`: Specify a filename to print the anonymized dataset details.
- `-rpt`: Don't remove private tags (by default, private tags are removed).
- `-rc`: Don't remove curves (by default, curves are removed).
- `-ip <identifier_path>`: Path to a file containing custom patient/surgeon identifying tags.
- `--niftipath <nifti_output_path>`: Path to output NIFTI files after conversion.

## Examples

1. Basic usage (anonymize all DICOM files in a directory):

   ```
   python anonymizeScans.py -p /path/to/dicom/files
   ```

2. Anonymize files and save a report:

   ```
   python anonymizeScans.py -p /path/to/dicom/files --print anonymization_report.txt
   ```

3. Anonymize files without removing private tags:

   ```
   python anonymizeScans.py -p /path/to/dicom/files -rpt
   ```

4. Use custom identifiers and convert to NIFTI:
   ```
   python anonymizeScans.py -p /path/to/dicom/files -ip custom_identifiers.txt --niftipath /path/to/nifti/output
   ```

## Custom Identifiers

By default, the script anonymizes the following DICOM tags:

- Referring Physician's Name
- Performing Physician's Name
- Name of Physician(s) Reading Study
- Operators' Name
- Patient's Name
- Patient's Birth Date
- Patient's Sex
- Patient's Age
- Additional Patient History
- Patient's Size
- Patient's Weight

To use custom identifiers, create a text file with each identifier on a new line and use the `-ip` option when running the script.

## Output

The script will anonymize the DICOM files in place, modifying the original files. If the `--print` option is used, a report of the anonymized data will be saved to the specified file.

If the `--niftipath` option is used, the script will also convert the anonymized DICOM files to NIFTI format and save them in the specified directory.

## Verification

After anonymization, the script automatically runs `checkScanAnonymity.py` to verify that all identifying information has been removed. If any identifiers are found, an exception will be raised.

## Caution

Always make a backup of your original DICOM files before running this script, as the anonymization process modifies the files in place and is irreversible.

## Support

If you encounter any issues or have questions, please open an issue in the project's GitHub repository.
