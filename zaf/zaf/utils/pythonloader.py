import logging
import pkgutil

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def load_module_or_package(qualname):
    """
    Load a Python module or package.

    Returns the module or package on success. Otherwise, raises ImportError.
    """
    logger.debug('Loading module or package from qualified name %s', qualname)
    loader = pkgutil.find_loader(qualname)
    if loader is None:
        message = 'Cound not find loader for module: {qualname}'.format(qualname=qualname)
        logger.warning(message)
        raise ImportError(message)
    try:
        return loader.load_module()
    except Exception as e:
        message = 'Could not load module: {qualname}'.format(qualname=qualname)
        logger.warning(message)
        raise ImportError(str(e)) from e


def load_submodules_and_subpackages(root_package):
    """
    Given a root package, recursively loads all sub-modules and -packages.

    Returns a list of what was loaded on success. Otherwise, raises ImportError.
    """
    loaded = []
    for _, name, _ in pkgutil.walk_packages(root_package.__path__, root_package.__name__ + '.'):
        loaded.append(load_module_or_package(name))

    # workaround for problem where the modules are not correctly connected
    for module in loaded:
        setattr(root_package, module.__name__.rsplit('.', 1)[1], module)

    for module in filter(is_python_package, loaded):
        loaded.extend(load_submodules_and_subpackages(module))
    return loaded


def is_python_package(thing):
    # Python modules has __spec__ while packages has __path__.
    return hasattr(thing, '__path__')
