from clinica.iotools.converters.adni_to_bids.adni_to_bids import convert
from clinica.utils.exceptions import ClinicaParserError
from clinica.iotools.converters.adni_to_bids.adni_utils import ADNIModality


# varibles
dataset_directory = '/path/to/dataset'
bids_directory = '/path/to/bids'
clinical_data_directory = '/path/to/clinical_data'
subjects_list = None
clinical_data_only = False
modalities = None
xml_path = None
force_new_extraction = False
n_procs = None

# validation
if clinical_data_only and force_new_extraction:
    raise ClinicaParserError(
        "Arguments `clinical_data_only` and `force_new_extraction` are mutually exclusive."
    )

convert(
        dataset_directory,
        bids_directory,
        clinical_data_directory,
        clinical_data_only=clinical_data_only,
        subjects=subjects_list,
        modalities=modalities or list(ADNIModality),
        xml_path=xml_path,
        force_new_extraction=force_new_extraction,
        n_procs=n_procs,
    )