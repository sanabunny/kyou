python.install_sources(
    files('__init__.py', '__main__.py', 'application.py', 'models.py'),
    subdir: 'kyou',
)

configure_file(
    input: 'config.py.in',
    output: '@BASENAME@',
    configuration: conf,
    install_dir: python.get_install_dir(subdir: 'kyou'),
)

subdir('ui')
subdir('backends')
