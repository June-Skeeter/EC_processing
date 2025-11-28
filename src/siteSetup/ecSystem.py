import dataclasses
import numpy as np
from typing import Iterable
from dataclasses import dataclass, field, MISSING
from src.databaseObjects.defaultObjects import spatialObject,sensorObject

@dataclass(kw_only=True)
class ecSensor(sensorObject):
    # sensorModel: str = field(
    #     default = None,
    #     metadata = {
    #         'description': 'The sensor model, auto-filled from class name',
    # })
    sensorType: str = field(
        metadata={
            'description': 'type of sensor',
            'options': ['sonic','irga','soinc+irga','thermocouple']
    })    
    measurementHeight: float = field(
        default = None,
        metadata = {
            'description': 'Measurement height (Zm) in meters, required for Sonics, optional otherwise',
    })
    northOffset: float = field(
        default = None,
        metadata = {
            'description': 'Offset from North in degrees (clockwise)',
    })
    pathType: str = field(
        default = None,
        metadata={
            'description':['Closed or open path'],
            'options':['closed','open']
    })
    northwardSeparation: float = field(
        default = None,
        metadata = {
            'description':'Northward separation from reference sonic (in m) required for irgas, and any secondary sonics.  Calculated from x&y separation if not provided.',
    })
    eastwardSeparation: float = field(
        default = None,
        metadata = {
            'description':'Eastward separation from reference sonic (in m) required for irgas, and any secondary sonics.  Calculated from x&y separation if not provided.',
    })
    
    verticalSeparation: float = field(
        default = None,
        metadata = {
            'description':'Vertical separation from reference sonic (in m) required for irgas, and any secondary sonics.',
    })

    xSeparation: float = field(
        default = None,
        metadata = {
            'description':'Lateral separation from reference sonic (in m) parallel to the main axis of the sonic (towards mast/sonic head = positive).  See Fig D2 in (https://s.campbellsci.com/documents/us/manuals/easyflux-dl-cr6op.pdf) for example.  Required for irgas, and any secondary sonics to calculate northward/eastward separation if not provided.',
    })
    ySeparation: float = field(
        default = None,
        metadata = {
            'description':'Lateral separation from reference sonic (in m) perpendicular to the main axis of the sonic (right of mast/sonic head = positive).  See Fig D2 in (https://s.campbellsci.com/documents/us/manuals/easyflux-dl-cr6op.pdf) for example.  Required for irgas, and any secondary sonics to calculate northward/eastward separation if not provided.',
    })
    zSeparation: float = field(
        default = None,
        metadata = {
            'description':'Synonymous with Vertical separation from reference sonic (in m) required for irgas, and any secondary sonics.',
    })

    windFormat: str = field(
        default=None,
        metadata = {
            'description': 'Format of wind data (only supports uvw for now).  Required for EddyPro',
            'options':['uvw']
    })

    tubeLength: float = field(
        default = None,
        metadata = {
            'description':'Length of intake tube (only for closed path irgas)',
    })
    tubeDiameter: float = field(
        default = None,
        metadata = {
            'description':'Diameter of intake tube (only for closed path irgas)',
    })

    def __post_init__(self):
        if self.pathType != 'closed':
            self.tubeDiameter = None
            self.tubeLength = None
        elif self.tubeDiameter is None or self.tubeLength is None:
            self.logError('Must provide tube length & diameter for closed path sensors')
        
        if not self.zSeparation is None and self.verticalSeparation is None:
            self.verticalSeparation = self.zSeparation
        if self.xSeparation == 0.0 and self.ySeparation == 0.0:
            self.northwardSeparation,self.eastwardSeparation = 0.0, 0.0
        if self.verticalSeparation is None and not ( (self.xSeparation is None and self.ySeparation is None) or ( (self.eastwardSeparation is None and self.northwardSeparation is None))):
            self.logError("Must provide separation parameters, in either sonic coordinates (xSeparation, ySeparation, zSeparation) or geographic coordinates (northwardSeparation, eastwardSeparation, verticalSeparation)")
        if (self.northwardSeparation is None or self.eastwardSeparation is None) and self.northOffset is not None:
            self.geographicSeparation()
        if self.sensorModel is None:
            self.sensorModel = type(self).__name__

        super().__post_init__()

    def geographicSeparation(self):
        if self.northwardSeparation is None and self.eastwardSeparation is None:
            # Convert to radians
            # **Note**: north offset is relative to geographic (meteorologic) north, while x,y offsets are in cartesian coordinates.  To perform the coordinate rotation properly theta must be converted to cartesian coordinate (positive is counter-clockwise from the x axis)
            theta = np.deg2rad(270-self.northOffset)
            # Calculate counter-clockwise rotation matrix
            R = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
            # Evaluate rotation matrix.
            v = np.array([[self.xSeparation,self.ySeparation]])
            Rv = (R*v)
            Rv = Rv.sum(axis=1).round(3)
            self.northwardSeparation = float(Rv[1])
            self.eastwardSeparation = float(Rv[0])
        pass


@dataclass(kw_only=True)
class ecSystem(spatialObject):
    systemID: str
    measurementHeight: float = field(
        metadata = {
            'description': 'Measurement height (Zm) in meters, required for Sonics, optional otherwise',
    })
    northOffset: float = field(
        metadata = {
            'description': 'Offset from North in degrees (clockwise) of the reference sonic',
    })

    ecSensors: Iterable = field(
        default_factory = list
        )

    def __post_init__(self):
        self.systemID = f"{self.systemID}_EC_{self.index}"
        # Format sensor objects
        if dataclasses.is_dataclass(self.ecSensors):
            self.ecSensors = [self.ecSensors.toConfig()]
        elif type(self.ecSensors) is dict:
            self.ecSensors = list(self.ecSensors.values())
        for i,sonic in enumerate(self.ecSensors):
            if dataclasses.is_dataclass(sonic):
                self.ecSensors[i] = sonic.toConfig()

        super().__post_init__()

        sensorDict = {}
        for sensor in self.ecSensors:
            if 'measurementHeight' not in sensor or sensor['measurementHeight'] is None:
                sensor['measurementHeight'] = self.measurementHeight
            if 'northOffset' not in sensor or sensor['northOffset'] is None:
                sensor['northOffset'] = self.northOffset
            sensor = ecSensor.from_dict(sensor)
            while sensor.UID in sensorDict.keys():
                sensor.updateUID()
            sensorDict[sensor.UID] = sensor.toConfig(keepNull=False)
        self.ecSensors = sensorDict
            
@dataclass(kw_only=True)
class IRGASON(ecSensor):
    manufacturer: str = 'CSI'
    sensorType: str = 'soinc+irga'
    pathType: str = 'open'
    xSeparation: float = 0.0
    ySeparation: float = 0.0
    zSeparation: float = 0.0
    
@dataclass(kw_only=True)
class CSAT3(ecSensor):
    manufacturer: str = 'CSI'
    sensorType: str = 'sonic'
    xSeparation: float = 0.0
    ySeparation: float = 0.0
    zSeparation: float = 0.0

@dataclass(kw_only=True)
class LI7700(ecSensor):
    manufacturer: str = 'LICOR'
    sensorType: str = 'irga'
    pathType: str = 'open'

@dataclass(kw_only=True)
class LI7500(ecSensor):
    manufacturer: str = 'LICOR'
    sensorType: str = 'irga'
    tubeLength: float = 0.0
    tubeDiameter: float = 0.0
    pathType: str = 'open'


@dataclass(kw_only=True)
class LI7200(ecSensor):
    manufacturer: str = 'LICOR'
    sensorType: str = 'irga'
    tubeDiameter: float = 5.33
    pathType: str = 'closed'

@dataclass(kw_only=True)
class fwThermocouple(ecSensor):
    sensorType: str = 'thermocouple'