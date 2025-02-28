import pandas as pd
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Create MPRAGEMETA.csv from adni_metadata.csv')
    parser.add_argument('--input', type=str, required=True, help='Path to the adni_metadata.csv file')
    parser.add_argument('--output', type=str, default='MPRAGEMETA.csv', help='Path to the output MPRAGEMETA.csv file')
    return parser.parse_args()

def main(args):
    input_path = args.input
    output_path = args.output

    df = pd.read_csv(input_path)

    if "study_series_seriesLevelMeta_derivedProduct_relatedImage_relation" in df.columns:
        orig_proc = df["study_series_seriesLevelMeta_derivedProduct_relatedImage_relation"]
        orig_proc = orig_proc.apply(lambda x: "Processed" if x != "derived_from" else "Original")
    else:
        orig_proc = ["Original"] * len(df)

    df_out = pd.DataFrame()
    df_out['Orig/Proc'] = orig_proc
    df_out['SubjectID'] = df["subjectIdentifier"]
    df_out['Visit'] = df['visit_visitIdentifier']
    df_out['MagStrength'] = df["study_imagingProtocol_protocolTerm_protocol"]
    df_out['Sequence'] = df["study_imagingProtocol_description"]
    df_out['ScanDate'] = df["study_series_dateAcquired"]
    df_out['StudyID'] = df['study_studyIdentifier']
    df_out['SeriesID'] = df['study_series_seriesIdentifier']
    df_out['ImageUID'] = df['study_imagingProtocol_imageUID']

    df_out.to_csv(output_path, index=False)

if __name__ == "__main__":
    args = parse_args()
    main(args)