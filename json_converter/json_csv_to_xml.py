import os
from lxml import etree as ET
import argparse
import json
import re
import csv
from xml.dom import minidom


def derivation(reader, core_id):
    coord = None
    for row in reader:
        if core_id == str(row[0]):
            coord = (float(row[1]), float(row[2]))
    return coord


def convert_json_to_xml(files_to_process, coord_file, output_folder):
    """
        This function take a list of json files containing data about Tumor, Extraepithelial CD8+ Cell and
        Intraepithelial CD8+ Cell, a csv file containing the coordinates of the centroids of every hotspot
        and an output folder as input and create xml files that can be loaded in ASAP.
    """
    # interested features
    annotations = ['Tumor', 'Extraepithelial CD8+ Cell', 'Intraepithelial CD8+ Cell', 'Center of Mass']
    # color code of the features
    colors = {'Tumor': '#4d66cc', 'Extraepithelial CD8+ Cell': 'magenta', 'Intraepithelial CD8+ Cell': 'magenta',
              'Center of Mass': 'black'}

    # initiate xml_tree
    xml_tree = ET.Element('ASAP_Annotations')
    # Make the annotations and coordinates
    xml_annotations = ET.SubElement(xml_tree, 'Annotations')
    # Make the groups
    xml_annotation_groups = ET.SubElement(xml_tree, 'AnnotationGroups')

    # open csv file
    with open(coord_file) as csv_file:
        # read csv file
        reader = csv.reader(csv_file, delimiter=';')
        # remove .csv extension
        coord_name = os.path.basename(coord_file).rsplit('.', 1)[0]
        # output file, add .xml extension
        output_file = os.path.join(output_folder, f'{coord_name}_asap.xml')
        for file_to_process in files_to_process:
            # remove .json extension
            file_name = os.path.basename(file_to_process).rsplit('.', 1)[0]
            # get the core id of the json file
            core_id = re.search('.*_CoreID_(.*)', file_name).group(1)

            csv_file.seek(0)
            coord = derivation(reader, core_id)
            if coord:
                dx, dy = coord
                # open json file
                with open(file_to_process) as file:
                    # load json file
                    data = json.load(file)
                    objects = data['Objects_Data']
                    # make the hotspot group
                    xml_main_group = ET.SubElement(xml_annotation_groups, 'Group',
                                                   attrib={'Name': f'Core_ID_{core_id}', 'PartOfGroup': 'None',
                                                           'Color': '#64FE2E'})
                    xml_main_group_attrib = ET.SubElement(xml_main_group, 'Attributes')
                    for group in annotations:
                        # make the group
                        xml_group = ET.SubElement(xml_annotation_groups, 'Group',
                                                  attrib={'Name': f'{group}, Core_ID_{core_id}', 'PartOfGroup': f'Core_ID_{core_id}',
                                                          'Color': colors[group]})
                        xml_group_attrib = ET.SubElement(xml_group, 'Attributes')
                        for i, object in enumerate(objects):
                            if object['Classification'] == group:
                                # Tumour and CD8+ Cell (Polygons)
                                # annotation
                                annotation_attrib = {'Name': f'Annotation {i}', 'PartOfGroup': f'{group}, Core_ID_{core_id}',
                                                     'Color': colors[group], 'Type': 'Polygon'}
                                xml_annotation = ET.SubElement(xml_annotations, 'Annotation', annotation_attrib)
                                # ROI Points
                                xml_coordinates = ET.SubElement(xml_annotation, 'Coordinates')
                                # get the list of points
                                points = object['ROI_Points']
                                # iterate over the list of points
                                for j, point in enumerate(points):
                                    coord_attrib = {'Order': str(j), 'X': str(point[0] + dx), 'Y': str(point[1] + dy)}
                                    xml_coordinate = ET.SubElement(xml_coordinates, 'Coordinate', attrib=coord_attrib)
                            elif group == 'Center of Mass':
                                # Center of Mass (Dot)
                                annotation_attrib = {'Name': f'Annotation {i + len(objects)}', 'PartOfGroup': f'{group}, Core_ID_{core_id}',
                                                     'Color': colors[group], 'Type': 'Dot'}
                                # get coordinates of the center of mass
                                cmx, cmy = object['Center_of_Mass']
                                cm_attrib = {'Order': '0', 'X': str(cmx + dx), 'Y': str(cmy + dy)}
                                xml_annotation = ET.SubElement(xml_annotations, 'Annotation', annotation_attrib)
                                xml_coordinates = ET.SubElement(xml_annotation, 'Coordinates')
                                xml_coordinate = ET.SubElement(xml_coordinates, 'Coordinate', attrib=cm_attrib)
            else:
                print(f'No coordinates found for the core id {core_id}')

    # Write
    e = ET.ElementTree(xml_tree).write(output_file, pretty_print=True)


if __name__ == '__main__':
    # pass input folder of json files and output folder as program arguments
    parser = argparse.ArgumentParser('Input and output folder')
    parser.add_argument('--input_files_folder', type=str, help='directory of the json data files', required=True)
    parser.add_argument('--output_folder', type=str, help='directory of the output folder', required=True)
    parser.add_argument('--coordinates_file', type=str, help='path to csv coordinates file', required=True)
    args = parser.parse_args()

    # get the values of input and output folder
    input_dir = args.input_files_folder
    output_dir = args.output_folder
    coord_path = args.coordinates_file

    # get all files to process as a list
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if re.search('Masks_.*.json', f)]

    # if output folder given doesn't exist then create it
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # stop the process if input folder is empty
    assert len(files) > 0, f'There is no files to process in the directory {input_dir}'
    assert os.path.isfile(coord_path), f'{coord_path} is not a file'
    assert coord_path.endswith('.csv'), f'{coord_path} is not a csv file'
    # create xml files
    convert_json_to_xml(files, coord_path, output_dir)