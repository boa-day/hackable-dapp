import os.path

root_folder = os.path.abspath(f'{__file__}/..')
contract_out = f'{root_folder}/boa_day.nef'


def compile():
    from boa3.boa3 import Boa3

    Boa3.compile_and_save(path=f'{root_folder}/boa_day.py',
                          output_path=contract_out,
                          root_folder=root_folder,
                          debug=True)


if __name__ == '__main__':
    compile()
