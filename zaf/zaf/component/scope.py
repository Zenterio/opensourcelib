import logging
import threading

logger = logging.getLogger('zaf.component')


class ScopeError(Exception):
    pass


class Scope(object):
    # This is used to indicate that the context does not contain an instance of
    # some callable. The reason an object instance is used instead of None is
    # that a callable may return None, while the object instance is unique.
    NO_INSTANCE = object()

    def __init__(self, name, parent=None, data=None):
        self.parent = parent
        self.name = name
        self.data = data

        self._internal_scope_lock = threading.Lock()

        # Contexts are the context manager and generator objects
        # and instances are the values created by entering the contexts.

        # These are lists of tuples where the first element is an _InstanceId object
        # and the second is the value.
        # The reason why these are not dicts is that _InstanceId is not hashable.
        self._instances = []
        self._contexts = []
        self._instance_locks = []

        if self.parent is not None:
            if name in self.parent.hierarchy():
                raise ScopeError(
                    "Multiple scopes with name '{name}' in the same hierarchy".format(name=name))

    def find_ancestor(self, name):
        if name == self.name:
            return self
        elif self.parent is not None:
            return self.parent.find_ancestor(name)
        else:
            raise ScopeError("No scope found with name '{scope}'".format(scope=name))

    def hierarchy(self):
        if self.parent is not None:
            hierarchy = self.parent.hierarchy()
        else:
            hierarchy = []
        hierarchy.append(self.name)
        return hierarchy

    def get_instance(self, instance_id):
        for id, instance in self._instances:
            if id == instance_id:
                return instance
        return Scope.NO_INSTANCE

    def register_instance(self, instance_id, instance):
        if self.get_instance(instance_id) is not Scope.NO_INSTANCE:
            msg = 'Multiple instances of the same callable in the same scope is not allowed.'
            raise ScopeError(msg)
        self._instances.append((instance_id, instance))

    def register_context(self, instance_id, context):
        self._contexts.append((instance_id, context))

    def instantiation_lock(self, instance_id):
        with self._internal_scope_lock:
            for lock_instance_id, lock in self._instance_locks:
                if lock_instance_id == instance_id:
                    return lock

            lock = threading.Lock()
            self._instance_locks.append((instance_id, lock))
            return lock

    def instances(self):
        return self._instances

    def contexts(self):
        return self._contexts

    def __str__(self):
        return self.name

    def __repr__(self):
        return '->'.join(self.hierarchy())
