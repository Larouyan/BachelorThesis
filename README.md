# BachelorThesis
This repository contains my bachelor thesis for my computer science studies at University of Fribourg.

## Conversion json to xml for whole slide image (./json_converter/json_to_xml.py)
To convert data from json to xml for whole slide image, you need to use `json_to_xml.py` with the following command lines:
- `--input_files_folder`: Path to the folder of json files.
- `--output_folder`: Path to the output folder (folder where the xml files will be written, if it doesn't exist it will create one).
- `--hotspot_folder`: Path to the hotspot annotations folder (folder of xml files containing coordinates of the hotspot).

## Conversion json to xml for TMA (.(json_convert/json_csv_to_xml)
To convert data from json to xml for TMA, you need to use `json_csv_to_xml.py` with the following command lines:
- `--input_files_folder`: Path to the folder of json files.
- `--output_folder`: Path to the output folder (folder where the xml files will be written, if it doesn't exist it will create one).
- `--coordinates_file`: Path to the csv coordinates file (file containing the radius and coordinates of the center for each sample in the TMA).

## Conversion json to csv (./json_converter/json_to_xml.py)
To convert data from json to csv you need to use `json_to_csv.py` with the following command lines:
- `--input_files_folder`: Path to the folder of json files.
- `--output_folder`: Path to the output folder (folder where the csv files will be written, if it doesn't exist it will create one).

### Environment
You can set up the conda environment in the directory "./json_converter" by using the following command: `conda env create -f environment.yml`

## Graph Visualisation (./graph_visualisation)
To run the application you simply have to use the `graph_viewer.py` and then you can directly pass in the app the folders containing gxl files and image files. The panels on the right (Node Style/Edge Style) are used to custom nodes and edges of the graph. On the botton you can choose the transparency of the hotspot image, the scaling (Factor by which the x and y coordinates should be multiplied) and color_by_feature (if None -> every node has the same color else every feature node has is own color and can be chosen on the Node Style panel). There is also a save button in order to save the current image after editing it where you just have to specify an output directory.

### Environment
You can set up the conda environment in the directory "./graph_visualisation" by using the following command: `conda env create -f environment.yml`
