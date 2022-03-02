import glob
import os
from lxml import etree as ET
import argparse
import re
import json


def convert_json_to_xml(file_to_process):
    """
        this function take a json file containing data about Tumor, Extraepithelial CD8+ Cell and
        Intraepithelial CD8+ Cell as input and create a xml file that can be loaded in ASAP.
    """
    # interested areas
    annotations = ['Tumor', 'Extraepithelial CD8+ Cell', 'Intraepithelial CD8+ Cell']
    # color code of the interested areas
    colors = {'Tumor': '#4d66cc', 'Extraepithelial CD8+ Cell': 'magenta', 'Intraepithelial CD8+ Cell': 'magenta'}

    # initiate xml_tree
    xml_tree = ET.Element('ASAP_Annotations')
    # Make the annotations and coordinates
    xml_annotations = ET.SubElement(xml_tree, 'Annotations')
    # Make the groups
    xml_annotation_groups = ET.SubElement(xml_tree, 'AnnotationGroups')

    # open json file
    with open(file_to_process) as file:
        # load json file
        data = json.load(file)
        for group in annotations:
            for object in data['Objects_Data']:
                if object['Classification'] == group:
                    



    # print(ET.tostring(xml_tree))


if __name__ == '__main__':
    path = 'C:/Users/Maintenant Pret/Desktop/Unifr/Bachelor/data/' \
           'export/Masks_00.2205_1D_AE1_AE3_CD8-level0-hotspot.json'
    convert_json_to_xml(path)
