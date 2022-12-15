import os
import argparse
import re
import json
import csv


def convert_json_to_csv(files_to_process, output_folder):
    """
        This function take a list of json files containing data about Tumor, Extraepithelial CD8+ Cell and
        Intraepithelial CD8+ Cell and an output folder as input and create a .CSV files of the interested features
        in the output folder.

        :param files_to_process: list of path to json files containing annotations.
        :param output_folder: path to the output directory.
    """
    features = ['Object_Index', 'Classification', 'Area', 'Circularity', 'Number_Cells', 'Perimeter', 'Solidity']
    for file_to_process in files_to_process:
        # remove .json extension
        file_name = os.path.basename(os.path.splitext(file_to_process)[0])
        # add .xml extension
        output_file = os.path.join(output_folder, f'{file_name}.csv')
        # open json file
        with open(file_to_process) as file:
            # load json file
            data = json.load(file)
            objects = data['Objects_Data']
            with open(output_file, 'w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, delimiter=';', fieldnames=features)
                writer.writeheader()
                for object in objects:
                    row = {feature: object[feature] for feature in features}
                    writer.writerow(row)


if __name__ == '__main__':
    # pass input folder of json files and output folder as program arguments
    parser = argparse.ArgumentParser('Input and output folder')
    parser.add_argument('--input_files_folder', type=str, help='directory of the json data files', required=True)
    parser.add_argument('--output_folder', type=str, help='directory of the output folder', required=True)
    args = parser.parse_args()

    # get the values of input and output folder
    input_dir = args.input_files_folder
    output_dir = args.output_folder

    # get all files to process as a list
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if re.search('Masks_.*-level0-hotspot.json', f)]
    # if output folder given doesn't exist then create it
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # stop the process if input folder is empty
    assert len(files) > 0, f'There is no files to process in the directory {input_dir}'
    # create xml files
    convert_json_to_csv(files, output_dir)
