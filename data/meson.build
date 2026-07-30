desktop_file = configure_file(
  input: 'page.fuwa.kyou.desktop.in',
  output: '@PLAINNAME@',
  configuration: conf,
)

desktop_file = i18n.merge_file(
  input: desktop_file,
  output: f'@app_id@.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: get_option('datadir') / 'applications',
)

test('Validate desktop file', desktop_utils, args: desktop_file)

configure_file(
  input: 'page.fuwa.kyou.gschema.xml.in',
  output: f'@app_id@.gschema.xml',
  configuration: conf,
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas',
)

test(
  'Validate schema file',
  compile_schemas,
  args: ['--strict', '--dry-run', meson.current_source_dir()],
)

appstream_file = configure_file(
  input: 'page.fuwa.kyou.metainfo.xml.in',
  output: '@PLAINNAME@',
  configuration: conf,
)

appstream_file = i18n.merge_file(
  input: appstream_file,
  output: f'@app_id@.metainfo.xml',
  po_dir: '../po',
  install: true,
  install_dir: get_option('datadir') / 'metainfo',
)

test(
  'Validate appstream file',
  appstreamcli,
  args: ['validate', '--no-net', '--explain', appstream_file],
)

configure_file(
  input: 'page.fuwa.kyou.service.in',
  output: f'@app_id@.service',
  configuration: conf,
  install_dir: get_option('datadir') / 'dbus-1' / 'services',
)

configure_file(
  input: 'kyou.in',
  output: '@BASENAME@',
  configuration: conf,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x',
)

resource = configure_file(
  input: 'data.gresource.xml.in',
  output: '@BASENAME@',
  configuration: conf,
)

gnome.compile_resources(
  'data',
  resource,
  gresource_bundle: true,
  install: true,
  install_dir: resourcedir,
  dependencies: appstream_file,
)

fonts = files(
  'fonts/Fraunces/Fraunces-Italic-VariableFont_SOFT,WONK,opsz,wght.ttf',
  'fonts/Fraunces/Fraunces-VariableFont_SOFT,WONK,opsz,wght.ttf',
  'fonts/Fredoka/Fredoka-VariableFont_wdth,wght.ttf',
  'fonts/Google_Sans_Code/GoogleSansCode-Italic-VariableFont_MONO,wght.ttf',
  'fonts/Google_Sans_Code/GoogleSansCode-VariableFont_MONO,wght.ttf',
  'fonts/Google_Sans_Flex/GoogleSansFlex-VariableFont_GRAD,ROND,opsz,slnt,wdth,wght.ttf',
)

install_data(
  fonts,
  install_dir: get_option('datadir') / 'fonts' / 'truetype' / 'kyou',
)

subdir('icons')
