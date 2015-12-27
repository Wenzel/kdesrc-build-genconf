import utils.process as process

def run(source, dest, install_prefix):
    args = [source, '-DCMAKE_INSTALL_PREFIX={}'.format(install_prefix)]
    return process.run('cmake', args, dest)
