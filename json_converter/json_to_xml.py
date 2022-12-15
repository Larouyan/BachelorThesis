import os
from lxml import etree as ET
import argparse
import json
import re
from xml.dom import minidom


def convert_json_to_xml(files_to_process, hotspot_folder, output_folder):
    """
        This function take a list of json files containing data about Tumor, Extraepithelial CD8+ Cell and
        Intraepithelial CD8+ Cell, a hotspot folder of xml files containing the coordinates of the hotspots
        and an output folder as input and create xml files that can be loaded in ASAP in the output folder.

        :param files_to_process: list of path to json files containing annotations.
        :param hotspot_folder: path to the directory containing the xml files with the coordinates of the hotspots.
        :param output_folder: path to the output directory.
    """
    # interested features
    annotations = ['Tumor', 'Extraepithelial CD8+ Cell', 'Intraepithelial CD8+ Cell', 'Center of Mass', 'hotspot']
    # color code of the features
    colors = {'Tumor': '#4d66cc', 'Extraepithelial CD8+ Cell': 'magenta', 'Intraepithelial CD8+ Cell': 'magenta',
              'Center of Mass': 'black', 'hotspot': '#64FE2E'}

    hotspot_name = [os.path.splitext(os.path.basename(f))[0] for f in hotspot_folder]

    for file_to_process in files_to_process:
        # initiate xml_tree
        xml_tree = ET.Element('ASAP_Annotations')
        # Make the annotations and coordinates
        xml_annotations = ET.SubElement(xml_tree, 'Annotations')
        # Make the groups
        xml_annotation_groups = ET.SubElement(xml_tree, 'AnnotationGroups')

        # remove .json extension
        file_name = os.path.basename(file_to_process).rsplit('.', 1)[0]
        # add .xml extension
        output_file = os.path.join(output_folder, f'{file_name}_asap.xml')
        # open correct hotspot xml
        file_code = re.search('Masks_(.*)-level0-hotspot', file_name).group(1)
        if file_code in hotspot_name:
            # open hotspot xml file
            hotspot_file = minidom.parse(os.path.join(os.path.dirname(hotspot_folder[0]), file_code + '.xml'))
            # read coordinates
            coordinates = hotspot_file.getElementsByTagName('Coordinate')
            hotspot_coord = [(float(point.attributes['X'].value), float(point.attributes['Y'].value))
                             for point in coordinates]
            # extract top left corner coordinates
            dx, dy = hotspot_coord[0]
            # open json file
            with open(file_to_process) as file:
                # load json file
                data = json.load(file)
                objects = data['Objects_Data']
                for group in annotations:
                    # make the group
                    xml_group = ET.SubElement(xml_annotation_groups, 'Group',
                                              attrib={'Name': group, 'PartOfGroup': 'None', 'Color': colors[group]})
                    xml_group_attrib = ET.SubElement(xml_group, 'Attributes')
                    for i, object in enumerate(objects):
                        if object['Classification'] == group:
                            # Tumour and CD8+ Cell (Polygons)
                            # annotation
                            annotation_attrib = {'Name': f'Annotation {i}', 'PartOfGroup': group, 'Color': colors[group],
                                                 'Type': 'Polygon'}
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
                            annotation_attrib = {'Name': f'Annotation {i + len(objects)}', 'PartOfGroup': group,
                                                 'Color': colors[group], 'Type': 'Dot'}
                            # get coordinates of the center of mass
                            cmx, cmy = object['Center_of_Mass']
                            cm_attrib = {'Order': '0', 'X': str(cmx + dx), 'Y': str(cmy + dy)}
                            xml_annotation = ET.SubElement(xml_annotations, 'Annotation', annotation_attrib)
                            xml_coordinates = ET.SubElement(xml_annotation, 'Coordinates')
                            xml_coordinate = ET.SubElement(xml_coordinates, 'Coordinate', attrib=cm_attrib)
                        elif group == 'hotspot':
                            # Hotspot (Rectangle)
                            annotation_attrib = {'Name': f'Annotation {2 * len(objects)}', 'PartOfGroup': group,
                                                 'Color': colors[group], 'Type': 'Rectangle'}
                            xml_annotation = ET.SubElement(xml_annotations, 'Annotation', annotation_attrib)
                            xml_coordinates = ET.SubElement(xml_annotation, 'Coordinates')
                            for j, point in enumerate(hotspot_coord):
                                coord_attrib = {'Order': str(j), 'X': str(point[0]), 'Y': str(point[1])}
                                xml_coordinate = ET.SubElement(xml_coordinates, 'Coordinate', attrib=coord_attrib)
                            break

            # Write
            e = ET.ElementTree(xml_tree).write(output_file, pretty_print=True)
        else:
            print(f'There is no hotspot annotations check folder for {file_to_process}')


if __name__ == '__main__':
    # pass input folder of json files and output folder as program arguments
    parser = argparse.ArgumentParser('Input and output folder')
    parser.add_argument('--input_files_folder', type=str, help='directory of the json data files', required=True)
    parser.add_argument('--output_folder', type=str, help='directory of the output folder', required=True)
    parser.add_argument('--hotspot_folder', type=str, help='directory of hotspot coordinates folder', required=True)
    args = parser.parse_args()

    # get the values of input and output folder
    input_dir = args.input_files_folder
    output_dir = args.output_folder
    hotspot_dir = args.hotspot_folder

    # get all files to process as a list
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if re.search('Masks_.*-level0-hotspot.json', f)]
    # xml hotspot files
    hotspots = [os.path.join(hotspot_dir, f) for f in os.listdir(hotspot_dir) if f.endswith('.xml')]

    # if output folder given doesn't exist then create it
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # stop the process if input folder is empty
    assert len(files) > 0, f'There is no files to process in the directory {input_dir}'
    assert len(hotspots) >= len(files)
    # create xml files
    convert_json_to_xml(files, hotspots, output_dir)

