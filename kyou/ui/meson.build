python.install_sources(
    files('__init__.py', 'window.py', 'today_card.py', 'now_card.py', 'gap_row.py', 'add_item_dialog.py'),
    subdir: 'kyou' / 'ui',
)

blueprints = custom_target(
    input: files('window.blp', 'today-card.blp', 'now-card.blp', 'gap-row.blp', 'add-item-dialog.blp'),
    output: '.',
    command: [
        blueprint_compiler,
        'batch-compile',
        '--minify',
        '@OUTPUT@',
        '@CURRENT_SOURCE_DIR@',
        '@INPUT@',
    ],
)

resource = configure_file(
    input: 'ui.gresource.xml.in',
    output: '@BASENAME@',
    configuration: conf,
)

gnome.compile_resources(
    'ui',
    resource,
    gresource_bundle: true,
    install: true,
    install_dir: resourcedir,
    dependencies: blueprints,
)
