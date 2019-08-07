DEFAULT = [
    ('title', 'title'),
    ('DIAS:sensingStartDate', 'sensing_date')
]

SLC = [
    ('title', 'title'),
    ('eo:orbitDirection', 'orbit_direction'),
    ('eo:orbitNumber', 'relative_orbit'),
    ('eo:polarisationChannels', 'polarisation'),
    ('DIAS:sensingStartDate', 'sensing_date')
]

GRD = [
    ('title', 'title'),
    ('eo:orbitDirection', 'orbit_direction'),
    ('eo:orbitNumber', 'relative_orbit'),
    ('eo:polarisationChannels', 'polarisation'),
    ('DIAS:sensingStartDate', 'sensing_date')
]

L1C = [
    ('title', 'title'),
    ('eo:orbitDirection', 'orbit_direction'),
    ('eo:orbitNumber', 'relative_orbit'),
    ('DIAS:tileIdentifier', 'tile'),
    ('DIAS:sensingStartDate', 'sensing_date')
]

PRODUCT_MAPPINGS = {
    'default': DEFAULT,
    'SLC': SLC,
    'GRD': GRD,
    'L1C': L1C
}
