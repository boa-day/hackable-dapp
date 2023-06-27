if __name__ == '__main__':
    import json
    import os.path

    import compile

    test_folder = os.path.abspath(f'{__file__}/..')
    setup_folder = f'{test_folder}/neo-express'

    try:
        compile.compile()

        # update deploy invoke for testing
        with open(compile.contract_out, mode='rb') as nef_output:
            nef = nef_output.read()

        with open(compile.contract_out.replace('.nef', '.manifest.json')) as manifest_output:
            manifest = json.loads(manifest_output.read())  # to shorten the json string
            manifest = json.dumps(manifest, separators=(',', ':'))

        with open(f'{setup_folder}/deploy_args.txt', 'wb+') as deploy_args:
            from boa3_test.test_drive.testrunner import utils

            args = [
                utils.value_to_parameter(nef),
                utils.value_to_parameter(manifest)
            ]

            deploy_args.write(bytes(json.dumps(args, indent=4), 'utf-8'))

        # this WILL fail if cpm is not executed
        from boa3.boa3 import Boa3

        Boa3.compile_and_save(path=f'{test_folder}/TestContract.py',
                              output_path=f'{test_folder}/test_contract.nef',
                              root_folder=test_folder,
                              debug=True)

    except BaseException as e:
        raise e
