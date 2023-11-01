from abc import abstractmethod
from typing import List, Dict, Any
from enum import Enum
import inspect
import datetime
import dataclasses
import logging


log = logging.getLogger(__name__)


class ObjectBase:
    METADATA = {
        "required": True,
        "default": None,
        "accepted_values": None,
    }

    @classmethod
    def customize(cls, **kwargs):
        custom_metadata = dict(**cls.METADATA)
        custom_metadata.update(kwargs)

        class Customized(cls):
            METADATA = custom_metadata

        return Customized

    @classmethod
    def parse(cls, iterator) -> "ObjectBase":
        if cls.METADATA["required"] is False and iterator.get_remaining_size() == 0:
            return None
        return cls._parse(iterator)

    @classmethod
    @abstractmethod
    def _parse(cls, iterator) -> "ObjectBase":
        pass

    @abstractmethod
    def dump(self, datagram) -> None:
        pass

    @classmethod
    def build(cls, *args, **kwargs) -> "ObjectBase":
        instance = cls(*args, **kwargs)
        instance.validate()
        return instance

    @classmethod
    @abstractmethod
    def dump_default(cls, datagram) -> None:
        pass

    @abstractmethod
    def _json(self) -> Any:
        pass

    def validate(self) -> None:
        accepted_values = self.METADATA["accepted_values"]
        if accepted_values is None:
            return

        if inspect.isclass(accepted_values) and issubclass(accepted_values, Enum):
            accepted_values = {v.value for v in accepted_values}

        if self not in accepted_values:
            raise TypeError(f"{self} not in {accepted_values}")

    @classmethod
    def from_dataclass(cls, value) -> "ObjectBase":
        assert dataclasses.is_dataclass(value)
        return cls(**dataclasses.asdict(value))


class BaseModel(ObjectBase):
    def __init__(self, *args, **kwargs):
        if args:
            fields = self.get_fields()
            for name in kwargs:
                fields.pop(name, None)

            kwargs.update(dict(zip(fields.keys(), args)))

        fields = self.get_fields()

        for name, value in kwargs.items():
            if name not in fields:
                continue
            if value is None:
                assert fields[name].METADATA["required"] is False
                setattr(self, name, None)
            elif dataclasses.is_dataclass(value):
                setattr(self, name, fields[name].from_dataclass(value))
            elif isinstance(value, fields[name]):
                setattr(self, name, value)
            else:
                setattr(self, name, fields[name].build(value))

    @classmethod
    def get_fields(cls) -> "List[ObjectBase]":
        fields = {}
        for name, type_ in cls.__dict__.items():
            if inspect.isclass(type_) and issubclass(type_, ObjectBase):
                fields[name] = type_
        return fields

    def _json(self) -> Dict:
        result = {}
        for name, type_ in self.get_fields().items():
            value = getattr(self, name)
            if value is not None and not inspect.isclass(value):
                result[name] = value._json()
            else:
                result[name] = None
        return result

    @classmethod
    def _parse(cls, iterator) -> "BaseModel":
        kwargs = {}
        for name, type_ in cls.get_fields().items():
            kwargs[name] = type_.parse(iterator)
        return cls.build(**kwargs)

    def dump(self, datagram) -> None:
        for name, type_ in self.get_fields().items():
            value = getattr(self, name)
            if value is not None and not inspect.isclass(value):
                value.dump(datagram)
            else:
                type_.dump_default(datagram)

    @classmethod
    def dump_default(cls, datagram) -> None:
        for type_ in cls.get_fields().values():
            type_.dump_default(datagram)


class UInt8(ObjectBase, int):
    @classmethod
    def _parse(cls, iterator) -> "UInt8":
        return cls.build(iterator.get_uint8())

    def dump(self, datagram) -> None:
        datagram.add_uint8(self.__int__())

    @classmethod
    def dump_default(cls, datagram) -> None:
        pass

    def _json(self) -> int:
        return self.__int__()


class Float64(ObjectBase, float):
    @classmethod
    def _parse(cls, iterator) -> "Float64":
        return cls.build(iterator.get_float64())

    def dump(self, datagram) -> None:
        datagram.add_float64(self.__float__())

    @classmethod
    def dump_default(cls, datagram) -> None:
        pass

    def _json(self) -> float:
        return self.__float__()


class String(ObjectBase, str):
    @classmethod
    def _parse(cls, iterator) -> "String":
        return cls.build(iterator.get_string())

    def dump(self, datagram) -> None:
        datagram.add_string(self.__str__())

    @classmethod
    def dump_default(cls, datagram) -> None:
        pass

    def _json(self) -> str:
        return self.__str__()


class MultilineString(String):
    @classmethod
    def _parse(cls, iterator) -> "MultilineString":
        lines = iterator.get_uint8()
        value = "\n".join((iterator.get_string() for i in len(lines)))
        return cls.build(value)

    def dump(self, datagram) -> None:
        lines = self.__str__().splitlines()
        datagram.add_uint8(len(lines))
        for line in lines:
            datagram.add_string(line)

    @classmethod
    def dump_default(cls, datagram) -> None:
        pass


class DateTime(ObjectBase, datetime.datetime):
    FORMAT = "%H:%M:%S"

    @classmethod
    def _parse(cls, iterator) -> "MultilineString":
        data = iterator.get_float64()
        value = datetime.datetime.fromtimestamp(data)
        return cls.build(value)

    def dump(self, datagram) -> None:
        value = self.timestamp()
        datagram.add_float64(value)

    @classmethod
    def dump_default(cls, datagram) -> None:
        pass

    def _json(self, format_=None) -> str:
        format_ = format_ or self.FORMAT
        return self.strftime(format_)

    @classmethod
    def build(cls, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], datetime.datetime):
            dt = args[0]
            args = []
            kwargs = dict(
                year=dt.year,
                month=dt.month,
                day=dt.day,
                hour=dt.hour,
                minute=dt.minute,
                second=dt.second,
                microsecond=dt.microsecond,
                tzinfo=dt.tzinfo,
                fold=dt.fold,
            )
        return cls(*args, **kwargs)


class CustomizableList(ObjectBase):
    ELEMENT_CLS: ObjectBase

    def __init__(self, value=None, *args):
        self.data = []
        model = self.ELEMENT_CLS

        if value is not None:
            if isinstance(value, (tuple, list)):
                args = list(args) + list(value)
            else:
                args = list(args) + [value]

        for value in args:
            if isinstance(value, model):
                self.data.append(value)
            elif isinstance(value, (tuple, list)):
                self.data.append(model.build(*value))
            elif isinstance(value, dict):
                self.data.append(model.build(**value))
            elif dataclasses.is_dataclass(value):
                self.data.append(model.from_dataclass(value))
            else:
                self.data.append(model.build(value))

    def _json(self) -> Dict:
        return [x._json() for x in self.data]

    def append(self, element: "BaseModel"):
        assert isinstance(element, self.ELEMENT_CLS)
        self.data.append(element)

    @classmethod
    def _parse(cls, iterator) -> "BaseModel":
        data = []
        while iterator.get_remaining_size() > 0:
            data.append(cls.ELEMENT_CLS.parse(iterator))
        return cls.build(*data)

    def dump(self, datagram) -> None:
        for value in self.data:
            value.dump(datagram)

    @classmethod
    def dump_default(cls, datagram) -> None:
        pass

    @classmethod
    def from_dataclass(cls, value) -> "ObjectBase":
        assert dataclasses.is_dataclass(value)
        return cls(**dataclasses.asdict(value))


def ListOf(cls):
    class CustomizedList(CustomizableList):
        ELEMENT_CLS = cls

    return CustomizedList
