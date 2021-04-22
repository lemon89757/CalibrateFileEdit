# -*- coding: utf-8 -*-
from anytree import NodeMixin
from intervals import FloatInterval


class CalibrateFile:
    def __init__(self, channel_number=0, rev_depends=None, depends=None, channels=None):
        self._channel_number = channel_number
        self._rev_depends = rev_depends
        self._depends = depends
        self._channels = channels

    @property
    def channel_number(self):
        return self._channel_number

    @channel_number.setter
    def channel_number(self, value):
        if type(value) != int:
            raise ValueError
        self._channel_number = value

    @property
    def rev_depends(self):
        return self._rev_depends

    @rev_depends.setter
    def rev_depends(self, value):
        if not all([isinstance(x, RevDepend) for x in value]):
            raise ValueError
        self._rev_depends = value

    @property
    def depends(self):
        return self._depends

    @depends.setter
    def depends(self, value):
        if not isinstance(value, Depends):
            raise ValueError
        self._depends = value

    @property
    def channels(self):
        return self._channels

    @channels.setter
    def channels(self, value):
        if not all([isinstance(x, Channel) for x in value]):
            raise ValueError
        self._channels = value

    # def find_entry_dependency(self, entry):
    #     for dependency in self._depends:
    #         if entry == dependency.index:
    #             return dependency

    # def find_next_dependency(self, transfer_number):
    #     if transfer_number < 0:
    #         raise ValueError
    #     else:
    #         for dependency in self._depends:
    #             if transfer_number == dependency.index:
    #                 return dependency

    def find_hardware(self, channel_pos, calibrate_msg_pos, transfer_number):
        current_channel = None
        hardwares = None
        for channel in self._channels:
            if channel_pos == channel.channel_index:
                current_channel = channel
        for calibrate_msg in current_channel.channel_msgs:
            if calibrate_msg_pos == calibrate_msg.index:
                hardwares = calibrate_msg.hardwares
        if transfer_number < 0:
            raise ValueError
        for hardware in hardwares:
            if hardware.index == -transfer_number - 1:
                return hardware

    def find_calibrate_factors(self, channel_pos, calibrate_msg_pos, transfer_number):
        current_channel = None
        calibrate_factors_list = None
        for channel in self._channels:
            if channel_pos == channel.channel_index:
                current_channel = channel
        for calibrate_msg in current_channel.channel_msgs:
            if calibrate_msg_pos == calibrate_msg.index:
                calibrate_factors_list = calibrate_msg.calibrate_factors
        return calibrate_factors_list[transfer_number]


class RevDepend:
    def __init__(self, calibrate_parameter_id=0, rev_depends=None):
        self._calibrate_parameter_id = calibrate_parameter_id
        self._rev_depends = rev_depends

    @property
    def calibrate_parameter_id(self):
        return self._calibrate_parameter_id

    @calibrate_parameter_id.setter
    def calibrate_parameter_id(self, value):
        if type(value) != int:
            raise ValueError
        self._calibrate_parameter_id = value

    @property
    def rev_depends(self):
        return self._rev_depends

    @rev_depends.setter
    def rev_depends(self, value):
        if type(value) != list:
            raise ValueError
        self._rev_depends = value


class Depends:
    def __init__(self, entry=None):
        self._depends = []
        self._entry = entry

    @property
    def entry(self):
        return self._entry

    @entry.setter
    def entry(self, value):
        if type(value) != int:
            raise ValueError
        self._entry = value

    def __iter__(self):
        self._count = 0
        self.entry_depend = None
        self.dependencies = []
        return self

    def __next__(self):
        if self._count == 0:
            for depend in self._depends:
                if self._entry == depend.parameter_index:
                    self._count += 1
                    self.entry_depend = depend
                    return self.entry_depend
        elif self._count == 1:
            for segment in self.entry_depend.parameter_segments:
                for depend in self._depends:
                    if segment.transfer_number == depend.parameter_index:
                        self._count += 1
                        self.dependencies.append(depend)
            return self.dependencies
        else:
            dependencies = []
            for dependency in self.dependencies:
                for segment in dependency.parameter_segments:
                    for depend in self._depends:
                        if segment.transfer_number < 0:
                            pass
                        elif segment.transfer_number == depend.parameter_index:
                            dependencies.append(depend)
            self.dependencies = dependencies
            if len(self.dependencies) == 0:
                raise StopIteration
            return self.dependencies

    def append(self, value):
        if isinstance(value, Depend):
            raise ValueError
        else:
            self._depends.append(value)

    def delete(self, value):
        if isinstance(value, Depend):
            raise ValueError
        for depend in self._depends:
            if value.parameter_index == depend.parameter_index:
                self._depends.remove(value)


class Depend:
    def __init__(self, parameter_id=0, parameter_index=0, parameter_segments=None):
        self._parameter_id = parameter_id
        self._parameter_index = parameter_index
        self._parameter_segments = parameter_segments

    @property
    def parameter_id(self):
        return self._parameter_id

    @parameter_id.setter
    def parameter_id(self, value):
        if type(value) != int:
            raise ValueError
        self._parameter_id = value

    @property
    def parameter_index(self):
        return self._parameter_index

    @parameter_index.setter
    def parameter_index(self, value):
        if type(value) != int:
            raise ValueError
        self._parameter_index = value

    @property
    def parameter_segments(self):
        return self._parameter_segments

    @parameter_segments.setter
    def parameter_segments(self, value):
        if not all([isinstance(x, DependencySegment) for x in value]):
            raise ValueError
        self._parameter_segments = value


class DependencySegment:
    def __init__(self, transfer_number=0, segment=None):
        self._segment = segment
        self._transfer_number = transfer_number

    @property
    def segment(self):
        return self._segment

    @segment.setter
    def segment(self, value):
        if type(value) != FloatInterval:
            raise ValueError
        self._segment = value

    @property
    def transfer_number(self):
        return self._transfer_number

    @transfer_number.setter
    def transfer_number(self, value):
        if type(value) != int:
            raise ValueError
        self._transfer_number = value


class CalibrateFileDependencyNode(Depend, NodeMixin):
    def __init__(self, parameter_id=0, parameter_index=0, parameter_segment=None):
        super(CalibrateFileDependencyNode, self).__init__(parameter_id=parameter_id, parameter_index=parameter_index)
        self._parameter_segment = parameter_segment
        self.parent = None
        self.children = None

    @property
    def parameter_segment(self):
        return self._parameter_segment

    @parameter_segment.setter
    def parameter_segment(self, value):
        if not isinstance(value, DependencySegment):
            raise ValueError
        self._parameter_segment = value


class Channel:
    def __init__(self, channel_index=0, channel_msgs=None):
        self._channel_index = channel_index
        self._channel_msgs = channel_msgs

    @property
    def channel_index(self):
        return self._channel_index

    @channel_index.setter
    def channel_index(self, value):
        if type(value) != int:
            raise ValueError
        self._channel_index = value

    @property
    def channel_msgs(self):
        return self._channel_msgs

    @channel_msgs.setter
    def channel_msgs(self, value):
        if not all([isinstance(x, CalibrateMsg) for x in value]):
            raise ValueError
        self._channel_msgs = value


class CalibrateMsg:
    def __init__(self, index=0, calibrate_parameter_id=0, entry=0, dependencies=None, model=0,
                 join_parameters=None, hardwares=None, calibrate_factors=None):
        self._index = index
        self._calibrate_parameter_id = calibrate_parameter_id
        self._entry = entry
        self._dependencies = dependencies
        self._model = model
        self._join_parameters = join_parameters
        self._hardwares = hardwares
        self._calibrate_factors = calibrate_factors

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        if type(value) != int:
            raise ValueError
        self._index = value

    @property
    def calibrate_parameter_id(self):
        return self._calibrate_parameter_id

    @calibrate_parameter_id.setter
    def calibrate_parameter_id(self, value):
        if type(value) != int:
            raise ValueError
        self._calibrate_parameter_id = value

    @property
    def entry(self):
        return self._entry

    @entry.setter
    def entry(self, value):
        if type(value) != int:
            raise ValueError
        self._entry = value

    @property
    def dependencies(self):
        return self._dependencies

    @dependencies.setter
    def dependencies(self, value):
        if type(value) != list:
            raise ValueError
        self._dependencies = value

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        if type(value) != int:
            raise ValueError
        self._model = value

    @property
    def join_parameters(self):
        return self._join_parameters

    @join_parameters.setter
    def join_parameters(self, value):
        if type(value) != list:
            raise ValueError
        self._join_parameters = value

    @property
    def hardwares(self):
        return self._hardwares

    @hardwares.setter
    def hardwares(self, value):
        if not all([isinstance(x, Hardware)] for x in value):
            raise ValueError
        self._hardwares = value

    @property
    def calibrate_factors(self):
        return self._calibrate_factors

    @calibrate_factors.setter
    def calibrate_factors(self, value):
        if type(value) != list:
            raise ValueError
        self._calibrate_factors = value


class Hardware:
    def __init__(self, index=0, hardware_segments=None):
        self._index = index
        self._hardware_segments = hardware_segments

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        if type(value) != int:
            raise ValueError
        self._index = value

    @property
    def hardware_segments(self):
        return self._hardware_segments

    @hardware_segments.setter
    def hardware_segments(self, value):
        if not all([isinstance(x, HardwareSegment) for x in value]):
            raise ValueError
        self._hardware_segments = value


class HardwareSegment:
    def __init__(self, segment=None, transfer_number=0):
        self._segment = segment
        self._transfer_number = transfer_number

    @property
    def segment(self):
        return self._segment

    @segment.setter
    def segment(self, value):
        if type(value) != FloatInterval:
            raise ValueError
        self._segment = value

    @property
    def transfer_number(self):
        return self._transfer_number

    @transfer_number.setter
    def transfer_number(self, value):
        if type(value) != int:
            raise ValueError
        self._transfer_number = value


class CalibrateFileHardwareNode(Hardware, NodeMixin):
    def __init__(self, index=0, hardware_segment=None):
        super(CalibrateFileHardwareNode, self).__init__(index=index)
        self._segment = hardware_segment
        self.parent = None
        self.children = None

    @property
    def segment(self):
        return self._segment

    @segment.setter
    def segment(self, value):
        if not isinstance(value, HardwareSegment):
            raise ValueError
        self._segment = value


class CalibrateFactor:
    def __init__(self, calibrate_factor=None):
        self._content = calibrate_factor

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if type(value) != list:
            raise ValueError
        self._content = value


class CalibrateFileFactorNode(CalibrateFactor, NodeMixin):
    def __init__(self, calibrate_factor=None):
        super(CalibrateFileFactorNode, self).__init__(calibrate_factor=calibrate_factor)
        self.parent = None

    # @property
    # def parent_node(self):
    #     return self._parent_node
    #
    # @parent_node.setter
    # def parent_node(self, value):
    #     if not isinstance(value, CalibrateFileHardwareNode):
    #         raise ValueError
    #     self._parent_node = value


class CalibrateParameter:
    def __init__(self, parameter_id=0, entry=0):
        self._parameter_id = parameter_id
        self._entry = entry

    @property
    def parameter_id(self):
        return self._parameter_id

    @parameter_id.setter
    def parameter_id(self, value):
        if type(value) != int:
            raise ValueError
        self._parameter_id = value

    @property
    def entry(self):
        return self._entry

    @entry.setter
    def entry(self, value):
        if type(value) != int:
            raise ValueError
        self._entry = value


class CalibrateFileRootNode(CalibrateParameter, NodeMixin):
    def __init__(self, parameter_id=0, entry=0, child_node=None):
        super().__init__(parameter_id=parameter_id, entry=entry)
        self.children = child_node
