project(
    'kyou',
    version: '49.0',
    meson_version: '>= 1.1.0',
    default_options: ['warning_level=2', 'werror=false'],
)

i18n = import('i18n')
gnome = import('gnome')
python = import('python').find_installation('python3')

blueprint_compiler = find_program('blueprint-compiler')
desktop_utils = find_program(
    'desktop-file-validate',
    required: false,
    disabler: true,
)
compile_schemas = find_program(
    'glib-compile-schemas',
    required: false,
    disabler: true,
)
appstreamcli = find_program('appstreamcli', required: false, disabler: true)

granite_dep = dependency('granite-7', version: '>= 7.0.0', required: false)

localedir = get_option('prefix') / get_option('localedir')
bindir = get_option('prefix') / get_option('bindir')
resourcedir = python.get_install_dir() / 'kyou' / 'resources'

app_id = 'page.fuwa.kyou'
prefix = '/page/fuwa/kyou'

conf = configuration_data(
    {
        'PYTHON': python.full_path(),
        'APP_ID': app_id,
        'PREFIX': prefix,
        'LOCALEDIR': localedir,
        'BINDIR': bindir,
    },
)

subdir('data')
subdir('kyou')
subdir('po')

gnome.post_install(
    glib_compile_schemas: true,
    gtk_update_icon_cache: true,
    update_desktop_database: true,
)
