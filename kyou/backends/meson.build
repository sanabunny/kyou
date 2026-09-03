python.install_sources(
    files('__init__.py'),
    subdir: 'kyou' / 'backends',
)

if host_machine.system() == 'darwin'
    python.install_sources(
        files('eventkit.py'),
        subdir: 'kyou' / 'backends',
    )
endif
