"""This module defines functions and classes for working with "ctypes.Array".

Key components:
Abstract class "BaseArray",
it defines the basic functionality for working with arrays.

The "Arrayc" class is a subclass of "BaseArray",
it wraps and manipulates "ctypes.Array".

The best way to create an "Arrayc" object is with the "arrayc" function,
it is more high-level and reliable.

Write help(arrayc.arrayc) for help with this function.

"""

import itertools
import functools
import ctypes
import copy
import abc



_py2c_types = {
    int:     ctypes.c_longlong,
    float:   ctypes.c_longdouble,
    str:     ctypes.c_wchar_p,
    bytes:   ctypes.c_char_p,
    bool:    ctypes.c_bool,
    None:    ctypes.c_void_p,
}


class ArraycIterator:
    """Arrayc objects iterator class.

    Used this way - iter(<Arrayc object>).

    Constructor params:
        array_object: Any sequence can be specified as this parameter.

    Examples:
    >>> array_object = arrayc.arrayc([1, 2, 3])
    >>> array_iter = iter(array_object)
    
    """

    def __init__(self, array_object):
        self._index = 0
        if isinstance(array_object, ctypes.Array):
            self._stop = array_object._length_
        else:
            self._stop = array_object.length
        self._array_object = array_object
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._index < self._stop:
            item = self._array_object[self._index]
        else:
            raise StopIteration
        self._index += 1
        return item


class BaseArray(metaclass=abc.ABCMeta):
    """Base class for working with "ctypes.Array".

    This is an abstract class, you cannot create an object of this class
    The "BaseArray" class extends the "ctypes.Array" functionality.
    Adds some list methods, etc.

    """
    
    # Just stubs.
    length = 101
    arrtype = ctypes.c_void_p
    itemsize = 0

    @abc.abstractmethod
    def __setitem__(self, key, value, /):
        pass

    @abc.abstractmethod
    def __getitem__(self, key, /):
        pass
    
    @abc.abstractmethod
    def __delitem__(self, key, /):
        pass

    # Methods.
    def __repr__(self):
        iterable = self.tolist()
        arrtype = "ctypes.%s" % self.arrtype.__name__
        length = self.length
        repr_text = "arrayc(iterable=%s, arrtype=%s, length=%s)" % (
            iterable,
            arrtype,
            length,
        )
        return repr_text
    
    def __str__(self):
        list_obj = self.tolist()
        text = "%s" % list_obj
        return text
    
    def __iter__(self, /):
        return ArraycIterator(self)
    
    def __len__(self):
        return self.length

    def tolist(self):
        return list(self)
    
    def setitems(self, iterable):
        for i, j in zip(itertools.count(), iterable):
            self[i] = j
    
    def updateitems(self, iterable):
        if len(iterable) > self.length:
            error_message = ("self length is {0}, iterable length is {1}. " + \
                "Are not equal.").format(self.length, len(iterable))
            raise ValueError(error_message)
        # Checks if the call will raise an exception.
        arrtype = self.arrtype
        for item in iterable:
            # Then it was not the wrong value for iterable.
            if not isinstance(item, arrtype):
                arrtype(item)
        self.setitems(iterable)

    def clear(self, /):
        arrtype_obj = self.arrtype()
        #setitem = self._arrayobject.__setitem__
        for i in range(len(self)):
            self[i] = arrtype_obj
     
    def copy(self, /):
        return copy.copy(self)
         
    def count(self, value, /):
        list_obj = self.tolist()
        return list_obj.count(value)
     
    def index(self, value, start=0, stop=9223372036854775807, /):
        list_obj = self.tolist()
        return list_obj.index(value, start, stop)
    
    def pop(self, index, /):
        value = self[index]
        self[index] = self.arrtype()
        return value

    def remove(self, value, /):
        list_obj = self.tolist()
        index = list_obj.index(value)
        self[index] = self.arrtype()

    def reverse(self, /):
        list_obj = self.tolist()
        list_obj.reverse()
        self.setitems(list_obj)
    
    def sort(self, /, *, key=None, reverse=False):
        list_obj = self.tolist()
        list_obj.sort(key=key, reverse=reverse)
        self.setitems(list_obj)


class CtypesBaseArray:
    def __repr__(self):
        iterable = list(self)
        return "<_Array(%s)>" % iterable
    
    def __str__(self):
        iterable = list(self)
        return "%s" % iterable
    
    def __setattr__(self, name, value):
        error_message = "'{0}' object attribute '{1}' is read-only".format(
            self.__class__.__name__, name)
        raise AttributeError(error_message)

    def __delattr__(self, name):
        error_message = "'{0}' object attribute '{1}' is read-only".format(
            self.__class__.__name__, name)
        raise AttributeError(error_message)


def create_array(iterable, arrtype, length):
    name = '_Array'
    bases = (ctypes.Array, CtypesBaseArray)
    attrs = {
        '_length_': length,
        '_type_': arrtype,
    }
    _Array = type(name, bases, attrs)
    _array_object = _Array(*iterable)
    return _array_object


class Arrayc(BaseArray):

    def __init__(self, iterable=[], arrtype=ctypes.c_void_p, length=101, fixed=False):
        self._is_setattr_initialized = True
        array_object = create_array(iterable, arrtype, length)

        self.length = array_object._length_
        self.arrtype = array_object._type_
        self._arrayobject = array_object
        self._fixed = fixed
        self._setitem = array_object.__setitem__
        self._getitem = array_object.__getitem__
        self.itemsize = ctypes.sizeof(array_object._type_)
        self._is_setattr_initialized = False
    

    def __setattr__(self, name, value):
        initialized = '_is_setattr_initialized'
        if name == initialized or bool(getattr(self, initialized, False)):
            super(Arrayc, self).__setattr__(name, value)
        else:
            error_message = "'{0}' object attribute '{1}' is read-only".format(
                self.__class__.__name__, name)
            raise AttributeError(error_message)
    
    def __delattr__(self, name):
        error_message = "'{0}' object attribute '{1}' is read-only".format(
            self.__class__.__name__, name)
        raise AttributeError(error_message)
    
    def __setitem__(self, key, value, /):
        return self._setitem(key, value)

    def __getitem__(self, key, /):
        return self._getitem(key)
    
    def __delitem__(self, key, /):
        self[key] = self.arrtype()
    
    def __iter__(self):
        return ArraycIterator(self._arrayobject)
    
    @staticmethod
    def setarrayitems(array_, iterable):
        Arrayc.setitems(array_, iterable)

    def getexpanded(self, length=21, *, is_arrayc=True):
        if not isinstance(length, int):
            error_message = "length is integer parameter not - '{0}'".format(
                    length.__class__.__name__)
            raise TypeError(error_message)
        if length < 0:
            raise ValueError("param 'length' >= 0")
        if not isinstance(is_arrayc, bool):
            error_message = "'is_arrayc' is 'bool' object not '{0}'".format(
                is_arrayc.__class__.__name__)
            raise TypeError(error_message)
        arrtype = self.arrtype
        newlength = self.length + length
        if is_arrayc:
            array_object = Arrayc(self, arrtype, newlength)
        else:
            array_object = create_array(self, arrtype, newlength)
        return array_object
    
    def expand(self, length=21):
        if self._fixed:
            raise TypeError("array is fixed")
        self._is_setattr_initialized = True
        try:
            array_object = self.getexpanded(length, is_arrayc=False)
            self.length += length
            self._arrayobject = array_object
            self._setitem = array_object.__setitem__
            self._getitem = array_object.__getitem__
            
        finally:
            self._is_setattr_initialized = False
    
    def tolist(self):
        return list(self._arrayobject)
    
    def getarrayobject(self):
        return self._arrayobject


def equaltypes(x, y):
    if type(x) == type(y):
        return x
    else:
        error_message = "Object types are not equal."
        raise TypeError(error_message)


def get_itemstype_info(iterable):

    if len(iterable) == 0:
        return (True, None)
    if len(iterable) == 1:
        return (True, type(next(iter(iterable))))
    try:
        functools.reduce(equaltypes, iterable)

    except TypeError:
        return (False, None)
    commontype = type(next(iter(iterable)))
    return (True, commontype)


def get_items_types(iterable):
    return frozenset(map(type, iterable))


def arrayc(iterable=[], arrtype=None, length=-1, fixed=False):
    
    # Checks params:
    # Checks if it is iterable.
    iter(iterable)
    if not isinstance(length, int):
        error_message = "'length' param must be an 'int'"
        raise TypeError(error_message)
    if not isinstance(fixed, bool):
        error_message = "'fixed' param must be an 'bool'"
        raise TypeError(error_message)
    # Gets iterable items type information.
    is_static, commontype = get_itemstype_info(iterable)
    if is_static and arrtype is None:
        arrtype = commontype
    elif not is_static:
        error_message = "Object types are not equal."
        raise TypeError(error_message)
    if arrtype in arrayc._py2c_types:
        arrtype = arrayc._py2c_types[arrtype]
    if length == -1:
        length = len(iterable)
    # Check arrtype param.
    PyCSimpleType = ctypes.c_void_p.__class__
    if not isinstance(arrtype, PyCSimpleType):
        error_message = "Param 'arrtype' must have ctypes type."
        raise TypeError(error_message)
    # Create object.
    arrayc_object = Arrayc(iterable, arrtype, length, fixed)
    return arrayc_object

arrayc._py2c_types = copy.copy(_py2c_types)


__all__ = [
    'arrayc',  'Arrayc',
    'create_array', 'BaseArray',
]