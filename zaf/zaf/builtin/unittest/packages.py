class NoSuchExtension(Exception):
    pass


def find_packages(extension_names, extension_manager, application_name, application_package):
    packages = []

    if not extension_names:
        extensions = extension_manager.all_extensions
        packages.extend(_packages_from_extensions(extensions))
        packages.append(application_package)
    else:
        for extension_name in extension_names:
            if extension_name.lower() in [application_name]:
                packages.append(application_package)
            else:
                extensions = extension_manager.extensions_with_name(extension_name)
                packages.extend(_packages_from_extensions(extensions))

                if not extensions:
                    raise NoSuchExtension(
                        'Extension {extension} not found'.format(extension=extension_name))

    return _combine_packages(packages)


def in_any_package(module_or_package, packages):
    for package in packages:
        if module_or_package.startswith('{package}.'.format(package=package)):
            return True
    return False


def _packages_from_extensions(extensions):
    return list({extension.__module__.rsplit('.', 1)[0] for extension in extensions})


def _combine_packages(packages):
    return [package for package in set(packages) if not in_any_package(package, packages)]
