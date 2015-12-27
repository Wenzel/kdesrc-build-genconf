import utils.process as process

def install(build_dir):
    args = ['install']
    return process.run('make', args, build_dir)

