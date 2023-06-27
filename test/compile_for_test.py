import os.path


test_folder = os.path.abspath(f'{__file__}/..')


def compile_main_contract() -> str:
    import json

    import compile

    setup_folder = f'{test_folder}/neo-express'
    try:
        compile.compile()

        # update deploy invoke for testing
        with open(compile.contract_out, mode='rb') as nef_output:
            nef = nef_output.read()

        with open(compile.contract_out.replace('.nef', '.manifest.json')) as manifest_output:
            manifest = json.loads(manifest_output.read())  # to shorten the json string
            contract_name = manifest['name']
            manifest = json.dumps(manifest, separators=(',', ':'))

        from boa3_test.test_drive.testrunner import utils
        args = [
            utils.value_to_parameter(nef),
            utils.value_to_parameter(manifest),
            [  # test data
                '0x2FC11419B09ACD6DD2ADD94262C523E12022F567ECA29334A86F071ECE5E8557',
                '0x02E014F3EEF6368723B3FCE4C5228B000C6B4D8F7C1BC8FBEFBA53691EB33279C1'
            ]
        ]

        deploy_file_path = f'{setup_folder}/deploy.neo-invoke.json'
        with open(deploy_file_path, 'r') as deploy_file:
            deploy_invoke = json.loads(deploy_file.read())
            deploy_invoke[0]['args'] = args

        with open(deploy_file_path, 'wb+') as deploy_file:
            deploy_file.write(bytes(json.dumps(deploy_invoke, indent=2) + '\n', 'utf-8'))

        return contract_name

    except BaseException as e:
        raise e


def compile_test_contract():
    try:
        # this WILL fail if cpm is not executed
        from boa3.boa3 import Boa3

        Boa3.compile_and_save(path=f'{test_folder}/TestContract.py',
                              output_path=f'{test_folder}/test_contract.nef',
                              root_folder=test_folder,
                              debug=True)

    except BaseException as e:
        raise e


if __name__ == '__main__':
    compile_main_contract()
    compile_test_contract()
