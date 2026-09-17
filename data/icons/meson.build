apps_dir = get_option('datadir') / 'icons' / 'hicolor' / '@0@' / 'apps'
install_data(f'@app_id@.svg', install_dir: apps_dir.format('scalable'))
install_data(f'@app_id@-symbolic.svg', install_dir: apps_dir.format('symbolic'))

foreach size : ['32x32', '48x48', '64x64', '128x128', '256x256']
    install_data(
        size / f'@app_id@.png',
        install_dir: apps_dir.format(size),
    )
endforeach

resource = configure_file(
    input: 'icons.gresource.xml.in',
    output: '@BASENAME@',
    configuration: conf,
)

gnome.compile_resources(
    'icons',
    resource,
    gresource_bundle: true,
    install: true,
    install_dir: resourcedir,
)
