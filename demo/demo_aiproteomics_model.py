import pandas as pd

from aiproteomics.core.sequence import SequenceMapper, PHOSPHO_MAPPING, PROSIT_MAPPING
from aiproteomics.core.modeltypes import ModelParamsMSMS, ModelParamsRT, ModelParamsCCS, AIProteomicsModel
from aiproteomics.core.utils import build_spectral_library
from aiproteomics.models.dummy_models import generate_dummy_msms_model, generate_dummy_iRT_model, generate_dummy_ccs_model


if __name__ == "__main__":


    # INPUT:
    # Choose what sequence mapping you want to use
    seqmap = SequenceMapper(min_seq_len=7, max_seq_len=50, mapping=PHOSPHO_MAPPING)

    # OUTPUT:
    # Choose your model type (msms) and the parameters for its output
    params = ModelParamsMSMS(seq_len=50, ions=['y','b'], max_charge=2, neutral_losses=['', 'H3PO4'])

    # Make a compatible NN model
    nn_model, creation_meta = generate_dummy_msms_model(
        params=params,
        num_layers=6,
        num_heads=8,
        d_ff=2048,
        dropout_rate=0.1
    )

    # Build the model
    msmsmodel = AIProteomicsModel(seq_map=seqmap, model_params=params, nn_model=nn_model, nn_model_creation_metadata=creation_meta)

    # Save the model
    msmsmodel.to_dir("testmodelfrag/", overwrite=True)


    # Load the model back in as a new AIProteomicsModel instance
    reloaded_msms = AIProteomicsModel.from_dir("testmodelfrag/")

    # Check what's inside
    print(reloaded_msms)


    # -----------

    # Try making a phospho-style iRT model
    seqmap = SequenceMapper(min_seq_len=7, max_seq_len=50, mapping=PHOSPHO_MAPPING)
    params = ModelParamsRT(seq_len=50, iRT_rescaling_mean=101.11514, iRT_rescaling_var=46.5882)
    nn_model, creation_meta = generate_dummy_iRT_model(
        params=params,
        num_layers=6,
        num_heads=8,
        d_ff=2048,
        dropout_rate=0.1
    )
    rtmodel = AIProteomicsModel(seq_map=seqmap, model_params=params, nn_model=nn_model, nn_model_creation_metadata=creation_meta)
    rtmodel.to_dir("testmodelrt/", overwrite=True)
    reloaded_rt = AIProteomicsModel.from_dir("testmodelrt/")
    print(reloaded_rt)


    # -----------

    # Try making a phospho-style ion mobility model
    seqmap = SequenceMapper(min_seq_len=7, max_seq_len=50, mapping=PHOSPHO_MAPPING)
    params = ModelParamsCCS(seq_len=50)
    nn_model, creation_meta = generate_dummy_ccs_model(
        params=params,
        num_layers=6,
        num_heads=8,
        d_ff=2048,
        dropout_rate=0.1
    )
    ccsmodel = AIProteomicsModel(seq_map=seqmap, model_params=params, nn_model=nn_model, nn_model_creation_metadata=creation_meta)
    ccsmodel.to_dir("testmodelccs/", overwrite=True)
    reloaded_ccs = AIProteomicsModel.from_dir("testmodelccs/")
    print(reloaded_ccs)


    # -----------
    # Build a spectral library using these models

    # Use it to generate a spectral library
    input_peptides = pd.read_csv('peptides_to_predict.tsv', sep='\t')
    speclib_df = build_spectral_library(input_peptides, msms=reloaded_msms, rt=reloaded_rt, ccs=reloaded_ccs)

    print(speclib_df)

    speclib_df.to_csv('speclib.tsv', sep='\t')
