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
            manifest_json = json.loads(manifest_output.read())  # to shorten the json string
            contract_name = manifest_json['name']
            manifest = json.dumps(manifest_json, separators=(',', ':'))

        deploy_file_path = f'{setup_folder}/deploy.neo-invoke.json'
        update_file_path = f'{setup_folder}/update.neo-invoke.json'
        with open(deploy_file_path, 'r') as deploy_file:
            deploy_invoke = json.loads(deploy_file.read())
            args_on_file = deploy_invoke[0]['args']

            from boa3_test.test_drive.testrunner import utils
            args_on_file[0] = utils.value_to_parameter(nef)
            args_on_file[1] = utils.value_to_parameter(manifest)

        with open(deploy_file_path, 'wb+') as deploy_file:
            deploy_file.write(bytes(json.dumps(deploy_invoke, indent=2) + '\n', 'utf-8'))

        manifest_json['extra']['updated'] = True
        manifest = json.dumps(manifest_json, separators=(',', ':'))

        deploy_invoke[0]['contract'] = contract_name
        deploy_invoke[0]['operation'] = 'update'
        args_on_file[1] = utils.value_to_parameter(manifest)

        with open(update_file_path, 'wb+') as deploy_file:
            deploy_file.write(bytes(json.dumps(deploy_invoke, indent=2) + '\n', 'utf-8'))

        return contract_name

    except BaseException as e:
        raise e


def compile_test_contract():
    try:
        # this WILL fail if cpm is not executed
        from boa3.boa3 import Boa3

        Boa3.compile_and_save(path=f'{test_folder}/test_contract.py',
                              output_path=f'{test_folder}/test_contract.nef',
                              root_folder=test_folder,
                              debug=True)

    except BaseException as e:
        raise e


if __name__ == '__main__':
    compile_main_contract()
    compile_test_contract()
