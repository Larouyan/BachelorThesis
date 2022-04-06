# BachelorThesis
This repository contains my bachelor thesis for my computer science studies at University of Fribourg.

## Conversion json to xml (./json_converter/json_to_xml.py)
To convert data from json to xml you need to use `json_to_xml.py` with the following command lines:
- `--input_files_folder`: Path to the folder of json files.
- `--output_folder`: Path to the output folder (folder where the xml files will be written, if it doesn't exist it will create one).
- `--hotspot_folder`: Path to the hotspot annotations folder (folder of xml files containing coordinates of the hotspot).

## Conversion json to csv (./json_converter/json_to_xml.py)
To convert data from json to csv you need to use `json_to_csv.py` with the following command lines:
- `--input_files_folder`: Path to the folder of json files.
- `--output_folder`: Path to the output folder (folder where the csv files will be written, if it doesn't exist it will create one).

### Environment
You can set up the conda environment in this directory by using the following command: `conda env create -f environment.yml`
