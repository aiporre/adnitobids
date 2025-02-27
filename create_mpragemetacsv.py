import numpy as np
import pandas as pd
import argparse
import os
import xml.etree.ElementTree as ET
import json
import tqdm


def parse_args():
    parser = argparse.ArgumentParser(description='Create csv file for mprage meta data')
    parser.add_argument('--datadir', type=str, help='Directory containing the mprage files')
    return parser.parse_args()


def parse_data_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    def xml_to_dict(element):
        data_dict = {}
        for child in element:
            if len(child) > 0:
                data_dict[child.tag] = xml_to_dict(child)
            else:
                data_dict[child.tag] = child.text
        return data_dict

    return xml_to_dict(root)


# Function to flatten the nested dictionary
def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def create_df(xml_files, xml_pairs, one=False):
    df = None
    for xml_file in tqdm.tqdm(xml_files, total=len(xml_files), desc='Creating dataframe'):
        data = xml_pairs[xml_file]['project']['subject']
        flattened_data = flatten_dict(data)
        if df is None:
            df = pd.DataFrame([flattened_data])
        else:
            df = pd.concat([df, pd.DataFrame([flattened_data])], ignore_index=True)
        if one:
            break

    return df


def main(args):
    datadir = args.datadir
    print(f'datadir: {datadir}')
    xml_pairs = {}
    subjects = []
    xml_files = []
    for subject in os.listdir(datadir):
        if os.path.isdir(os.path.join(datadir, subject)):
            subjects.append(subject)
    # list of xml files
    for f in os.listdir(datadir):
        if f.endswith('.xml'):
            xml_files.append(f)
    print('number of subject found ', len(subject))
    print('number of xml files found ', len(xml_files))
    for xml_file in xml_files:
        xml_pairs[xml_file] = parse_data_xml(os.path.join(datadir, xml_file))
        break
    # get first and print pretty
    print(json.dumps(xml_pairs[xml_files[0]], indent=4))
    df = create_df(xml_files, xml_pairs, one=True)

    for c in df.columns.sort_values():
        print("--------------", c, "----------------")
        print(df[c])

    # do again but all the dataset
    for xml_file in tqdm.tqdm(xml_files, total=len(xml_files), desc='Parsing xml files'):
        xml_pairs[xml_file] = parse_data_xml(os.path.join(datadir, xml_file))
    df = create_df(xml_files, xml_pairs)
    df.to_csv('mprage_meta.csv', sep=',', index=False)


if __name__ == "__main__":
    args = parse_args()
    main(args)
