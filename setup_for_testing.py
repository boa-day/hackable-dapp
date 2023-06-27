if __name__ == '__main__':
    import json
    import os
    import subprocess

    from test import compile_for_test as test_compiler
    import compile as main_compiler

    # compile main contract
    main_contract_name = test_compiler.compile_main_contract()
    manifest_path = main_compiler.contract_out.replace('.nef', '.manifest.json')
    print()

    # deploy main contract
    result_code = os.system('neoxp batch -r ./test/neo-express/setup-main-contract.batch -i ../../default.neo-express')
    if result_code:
        exit(result_code)
    print()

    # get contract script hash
    output = subprocess.check_output(f'neoxp contract get {main_contract_name}'.split(' '),
                                     encoding='utf-8')
    main_contract_hash = json.loads(output)[0]['hash']

    # update script hash on the interface used by the test contract
    command = ("cpm --log-level DEBUG generate"
               f" -m {manifest_path}"
               f" -c {main_contract_hash}"
               f" -o {test_compiler.test_folder}/cpm_out/"
               " -l python")
    print(command)
    result_code = os.system(command)

    if result_code:
        exit(result_code)
    print()

    # compile test contract
    test_compiler.compile_test_contract()
    print()

    # deploy test contract
    result_code = os.system('neoxp batch ./test/neo-express/setup-test-contract.batch -i ../../default.neo-express')
    exit(result_code)
