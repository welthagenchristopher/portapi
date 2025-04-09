class Format:

    def __init__(self):
        self.nodata = 'No data'

    def _generate_dict(self, mapping, vessel): # Nothing too special here - iterative dictionary generation for formatting,
                                               # the json responses from the API. Honestly, If I had to do this I'd use,
                                               # the basemodel library.
        
        return {key: vessel.get(value, self.nodata) if isinstance(value, str) else value(vessel) for key, value in mapping.items()}

    def setvessel(self, vessel):
        
        mapping = {
            'name': 'vesselName',
            'reference': 'vesselVisitReference',
            'voyage in': 'inboundVoyage',
            'voyage out': 'outboundVoyage',
            'wharf': 'wharfName',
            'port': 'portCode',
            'arrival date': 'arrivalDatetime',
            'seaport cutoff': 'receivalCutoffSeaport',
            'inland cutoff': 'receivalCutoffInland',
            'departure date': 'departureDatetime',
            'line': 'vesselOperator',
        }
        return self._generate_dict(mapping, vessel)

    def invessel(self, vessel):
        
        mapping = {
            'name': 'vesselName',
            'reference': 'vesselVisitReference',
            'voyage out': 'outboundVoyage',
            'wharf': 'wharfName',
            'port': 'portCode',
            'arrival date': 'arrivalDatetime',
            'departure date': 'departureDatetime',
            'seaport receival': 'receivalCommenceSeaport',
            'inland receival': 'receivalCommenceInland',
            'seaport cutoff': 'receivalCutoffSeaport',
            'inland cutoff': 'receivalCutoffInland',
            'line': 'vesselOperator',
        }
        return self._generate_dict(mapping, vessel)

    def outvessel(self, vessel):
        
        mapping = {
            'name': 'vesselName',
            'reference': 'vesselVisitReference',
            'voyage out': 'outboundVoyage',
            'wharf': 'wharfName',
            'departure port': 'previousPortName',
            'departure date': 'departureDatetime',
            'line': 'vesselOperator',
        }
        return self._generate_dict(mapping, vessel)

    def incontainer(self, vessel):
        
        if not vessel.get('inlandPortArrivalDatetime'):
            mapping = {
                'container': 'containerNumber',
                'category': 'shipmentDirection',
                'weight': 'declaredWeight',
                'vessel': 'inboundVesselName',
                'line': 'containerOperatorName',
                'vessel arrival': lambda v: v.get('inboundVesselActualArrivalDatetime') or v.get('inboundVesselPublishedArrivalDatetime', self.nodata),
                'discharge port': 'dischargePortName',
                'discharge date': lambda v: v.get('dischargedDatetime', 'not yet discharged'),
                'line release': 'lineReleaseDatetime',
                'customs release': 'customsReleaseDatetime',
                'free time': 'lastFreeDatetime',
                'dehire depot': 'emptyReturnDepotName',
            }
        else:
            mapping = {
                'container': 'containerNumber',
                'category': 'shipmentDirection',
                'weight': 'declaredWeight',
                'vessel': 'inboundVesselName',
                'line': 'containerOperatorName',
                'inland port': 'dischargePortName',
                'vessel arrival': lambda v: v.get('inboundVesselActualArrivalDatetime') or v.get('inboundVesselPublishedArrivalDatetime', self.nodata),
                'inland port arrival': 'inlandPortArrivalDatetime',
                'inland port discharge': lambda v: v.get('dischargedDatetime', 'not yet discharged'),
                'line release': 'lineReleaseDatetime',
                'customs release': 'customsReleaseDatetime',
                'free time': 'lastFreeDatetime',
                'dehire depot': 'emptyReturnDepotName',
            }
        return self._generate_dict(mapping, vessel)

    def outcontainer(self, vessel):
        
        mapping = {
            'container': 'containerNumber',
            'category': 'shipmentDirection',
            'weight': 'declaredWeight',
            'vessel': 'outboundVesselName',
            'line': 'containerOperatorName',
            'destination port': 'destinationPortName',
        }
        return self._generate_dict(mapping, vessel)

if __name__ == '__main__':
    formatter = Format()
    sample_vessel = {'vesselName': 'Evergreen', 'vesselVisitReference': 'EV1234'}
    print(formatter.setvessel(sample_vessel))
