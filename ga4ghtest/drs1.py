from ga4gh.drs.cli.methods import get

def get_a_file():
    response = get(
        url='https://jade-terra.datarepo-prod.broadinstitute.org/ga4gh/drs/v1',
        object_id='v1_8285aea0-88fe-4bf7-9a60-2a45482a32f6_d3e82b4a-b720-4790-b7d1-9710040c5dda_91f5bd1c-e264-461e-8e6b-45188db4d715',
        authtoken='xxx')

    print(response)

    return response
