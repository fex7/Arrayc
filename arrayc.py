
import itertools
import functools
import ctypes
import copy
import abc



_types_ = {
    int:     ctypes.c_longlong,
    float:   ctypes.c_longdouble,
    str:     ctypes.c_wchar_p,
    bytes:   ctypes.c_char_p,
    bool:    ctypes.c_bool,
    None:    ctypes.c_void_p,
}


class ArraycIterator:
    def __init__(self, arrayc_object):
        self.index = 0
        self.stop = arrayc_object.length_
        self.arrayc_object = arrayc_object
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index < self.stop:
            item = self.arrayc_object[self.index]
        else:
            raise StopIteration
        self.index += 1
        return item


class AttributeProtector:
    def __init__(self, name):
        self.name = name
        self._array_initialized = False
    
    @property
    def array_initialized(self):
        return self._array_initialized
    
    @array_initialized.setter
    def array_initialized(self, value):
        if self._array_initialized:
            error_message = "Array object is initlized."
            raise ValueError(error_message)
        
        if not isinstance(value, bool):
            error_message = "Only logical object can be assigned"
            raise TypeError(error_message)
        
        self._array_initialized = value

    def __get__(self, instance, instance_type=None):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not self.array_initialized:
            instance.__dict__[self.name] = value
            self.array_initialized = True
        else:
            raise AttributeError("can't set attribute")

    def __delete__(self, instance):
        raise AttributeError("can't delete attribute") 


class BaseArray(abc.ABC):
    
    # Just stubs.
    _length_ = 101
    _type_ = ctypes.c_longlong
    length_ = _length_
    type_ = _type_

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
        arrtype = "ctypes.%s" % self.type_.__name__
        length = self.length_
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
        return self.length_

    def tolist(self):
        return list(self)
    
    def setitems(self, iterable):
        for i, j in zip(itertools.count(), iterable):
            self[i] = j
    
    def updateitems(self, iterable):
        if len(iterable) > self.length_:
            error_message = ("Array length is - {0}, iterable length is - {1}, " + \
                "it's uneven!").format(self.length_, len(iterable))
            raise ValueError(error_message)
        arrtype_type = self.type_
        for item in iterable:
            if not isinstance(item, arrtype_type):
                error_message = ("All elements of the iteration must be of" + \
                    "the same type as the elements of the array. " + \
                    "array type is '{0}'").format(arrtype_type.__name__)
                raise TypeError(error_message)
        self.setitems(iterable)

    def clear(self, /):
        arrtype_obj = self.type_()
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
        self[index] = self.type_()
        return value

    def remove(self, value, /):
        list_obj = self.tolist()
        index = list_obj.index(value)
        self[index] = self.type_()

    def reverse(self, /):
        list_obj = self.tolist()
        list_obj.reverse()
        self.setitems(list_obj)
    
    def sort(self, /, *, key=None, reverse=False):
        list_obj = self.tolist()
        list_obj.sort(key=key, reverse=reverse)
        self.setitems(list_obj)


def create_array(iterable=[], arrtype=ctypes.c_void_p, length=101):
    name = '_Array'
    bases = (ctypes.Array,)
    attrs = {
        '_length_': length,
        '_type_': arrtype,
    }
    _Array = type(name, bases, attrs)
    _array_object = _Array(*iterable)
    return _array_object


class Arrayc(BaseArray):

    type_ = AttributeProtector('_type_')
    length_ = AttributeProtector('_length_')
    _arrayobject = AttributeProtector('_arrayobject')

    def __init__(self, iterable=[], arrtype=ctypes.c_void_p, length=101):
        array_object = create_array(iterable, arrtype, length)
       
        self._length_ = array_object._length_
        self._type_ = array_object._type_
        self._arrayobject = array_object
       
        self._setitem = array_object.__setitem__
        self._getitem = array_object.__getitem__
    
    def __setitem__(self, key, value, /):
        return self._setitem(key, value)

    def __getitem__(self, key, /):
        return self._getitem(key)
    
    def __delitem__(self, key, /):
        self[key] = self.type_()

    @property
    def length_(self):
        return self._length_

    @property
    def type_(self):
        return self._type_

    @property
    def arrayobject(self):
        return self._arrayobject
    
    @arrayobject.setter
    def arrayobject(self, new_arrayc):
        if not isinstance(new_arrayc, self.arrayobject.__class__):
            error_message = "New array "
    
    @staticmethod
    def setarrayitems(array_, iterable):
        Arrayc.setitems(array_, iterable)

    def getexpanded(self, length=21, *, is_arrayc=True):
        if not isinstance(length, int):
            error_message = "Length is integer parameter not - '{0}'".format(
                    length.__class__.__name__)
            raise TypeError(error_message)
        arrtype = self.type_
        newlength = self.length_ + length
        if is_arrayc:
            array_object = Arrayc(self, arrtype, newlength)
        else:
            array_object = create_array(self, arrtype, newlength)
        return array_object
    
    #def expand(self, length):
      #  new_array_object = self.getexpanded(length, is_arrayc=True)


def equaltypes(x, y):
    if type(x) == type(y):
        return x
    else:
        err_msg = "Object types are not equal."
        raise TypeError(err_msg)


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


def arrayc(iterable=[], arrtype=None, length=-1):
    
    # Checks params
    # Checks if it is iterable.
    iter(iterable)
    if not isinstance(length, int):
        error_message = "The 'length' param must be an integer"
        raise TypeError(error_message)
    # Gets iterable items type information.
    is_static, commontype = get_itemstype_info(iterable)
    if is_static and arrtype is None:
        arrtype = commontype
    if not is_static:
        error_message = "Object types are not equal."
        raise TypeError(error_message)
    if arrtype in _types_:
        arrtype = _types_[arrtype]
    if length == -1:
        length = len(iterable)
    # Check arrtype param.
    PyCSimpleType = ctypes.c_void_p.__class__
    if not isinstance(arrtype, PyCSimpleType):
        error_message = "Param 'arrtype' must have ctypes type."
        raise TypeError(error_message)
    # Create Arrayc object.
    arrayc_object = Arrayc(iterable, arrtype, length)
    return arrayc_object


"""
class arraycf:
    def __init__(self, arrtype=ctypes.c_long, length=101, iterable=[]):
        name = 'Array'
        bases = (ctypes.Array, BaseArray, self.__class__)
        attrs = {
            '_length_': length,
            '_type_': arrtype,
        }

        Arraycf = type(name, bases, attrs)
"""