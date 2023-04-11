import time
from pyautocad import Autocad, APoint
import math
from math import atan

"""
Title: Stability Analysis of Structures
Author: Bhoshaga Ravi Chandran
Description: This script calculates the stability of an object and models it in 3D space, while producing a report

Resources:
    1. https://help.autodesk.com/view/ACD/2023/ENU/?guid=GUID-A060558E-092C-403D-8A63-276BAB901F5C
"""



class Model:
    def __init__(self, model, prop=None):
        self.max_width = 1
        self.geometry = model
        self.resisting = 0
        self.seismic_inertia_moment = 0
        self.overturning = None
        self.model = []
        self.soil_forces = None
        self.prop = None

        if prop:
            self.prop = prop
        else:
            self.set_values()

        self.acad = Autocad()
        self.name = self.acad.doc.Name

        # self.model = [{'id': 'base slab', 'height': 0.5, 'width': 6, 'length': 12, 'vol': '36.0', 'centroid': '(6.0, 3.0, 0.25)'}, {'id': 'left wall', 'height': 3, 'width': 6, 'length': 0.5, 'vol': '9.0', 'centroid': '(0.25, 3.0, 2.0)'}, {'id': 'right wall', 'height': 5, 'width': 6, 'length': 0.5, 'vol': '15.0', 'centroid': '(11.75, 3.0, 3.0)'}, {'id': 'front wall', 'height': 3, 'width': 0.5, 'length': 11, 'vol': '16.5', 'centroid': '(6.0, 0.25, 2.0)'}, {'id': 'wedge front wall', 'vol': '5.499999999999999', 'centroid': '(7.833333333333332, 0.25, 4.166666666666666)'}, {'id': 'back wall', 'height': 3, 'width': 0.5, 'length': 11, 'vol': '16.5', 'centroid': '(6.0, 5.75, 2.0)'}, {'id': 'wedge back wall', 'vol': '5.499999999999999', 'centroid': '(7.833333333333332, 5.75, 4.166666666666666)'}]
        self.box_extrude()

    def set_values(self):
        properties = {
            'g_conc': 150,  # pcf
            'pga_eff': 2/3 * 1.56,   # pga
            'g_active': 46,          # pcf
            'g_eq': 82,             # pcf
            'g_passive': 350,       # pcf
            'g_active_height': 5,   # ft
            'g_eq_height': 5,       # ft
            'g_passive_height': 0,  # ft
            'soil_width': 5
        }
        self.prop = properties

    def box_model(self):
        a1 = APoint(0, 0, 0)
        a2 = APoint(0, 8, 0)
        a3 = APoint(5, 8, 0)
        a4 = APoint(5, 0, 0)
        b1 = APoint(0, 0, 4)
        b2 = APoint(0, 8, 6)
        b3 = APoint(5, 8, 6)
        b4 = APoint(5, 0, 4)
        print(self.name)
        connections = [a1, a2, a3, a4, a1, b1, b2, b3, b4, b1]
        for i in range(len(connections)-1):
            p1 = connections[i]
            p2 = connections[i+1]
            self.acad.model.AddLine(p1, p2)

        connect_lines = [(a2, b2), (a3, b3), (a4, b4)]
        for a in connect_lines:
            p1 = a[0]
            p2 = a[1]
            self.acad.model.AddLine(p1, p2)

        a1 = APoint(-1, -1, 0)
        a2 = APoint(-1, 9, 0)
        a3 = APoint(6, 9, 0)
        a4 = APoint(6, -1, 0)
        b1 = APoint(-1, -1, 3.7)
        b2 = APoint(-1, 9, 6.3)
        b3 = APoint(6, 9, 6.3)
        b4 = APoint(6, -1, 3.7)
        print(self.acad.doc.Name)
        connections = [a1, a2, a3, a4, a1, b1, b2, b3, b4, b1]
        for i in range(len(connections)-1):
            p1 = connections[i]
            p2 = connections[i+1]
            self.acad.model.AddLine(p1, p2)

        connect_lines = [(a2, b2), (a3, b3), (a4, b4)]
        for a in connect_lines:
            p1 = a[0]
            p2 = a[1]
            self.acad.model.AddLine(p1, p2)
        self.box_extrude()

    # This function defines the geometry of the structure to be analyzed, draws on AutoCAD in 3D and calculates
    # properties. also creates a model of an object to be analyzed
    def box_extrude(self):
        # find max width
        for values in self.geometry.values():
            if 'width' in values:
                if values['width'] > self.max_width:
                    self.max_width = values['width']
        # for each geometry, draw them
        for key, value in self.geometry.items():
            if key == 'bs':
                # Add bottom slab
                bs = value
                base_slab_center = (bs['length'] / 2, bs['width'] / 2, bs['height'] / 2)
                slab = self.acad.model.AddBox(APoint(base_slab_center), bs['length'], bs['width'], bs['height'])
                slab.Color = 1
                bs['vol'] = str(slab.Volume)
                bs['centroid'] = slab.Centroid
                self.model.append(bs)
            elif key == 'ts':
                # Add top slab
                ts = value
                top_slab_center = (ts['length'] / 2, ts['width'] / 2, ts['height'] / 2 + bs['height'] + 9)
                top_slab = self.acad.model.AddBox(APoint(top_slab_center), ts['length'], ts['width'], ts['height'])
                if 'angle' in ts:
                    top_slab.Rotate3D(APoint(ts['length'], ts['width'], bs['height'] + 9),
                                      APoint(ts['length'], ts['width'] + 2, bs['height'] + 9), ts['angle'])
                top_slab.Color = 3
                ts['vol'] = str(top_slab.Volume)
                ts['centroid'] = top_slab.Centroid
                self.model.append(ts)
            elif key == 'lw':
                # Add left wall
                lw = value
                left_wall_center = (lw['length'] / 2, lw['width'] / 2, lw['height'] / 2 + bs['height'])
                left_wall = self.acad.model.AddBox(APoint(left_wall_center), lw['length'], lw['width'], lw['height'])
                left_wall.Color = 2
                lw['vol'] = str(left_wall.Volume)
                lw['centroid'] = left_wall.Centroid
                self.model.append(lw)
            elif key == 'rw':
                # Add right wall
                rw = value
                right_wall_center = (bs['length'] - rw['length'] / 2, rw['width'] / 2, rw['height'] / 2 + bs['height'])
                right_wall = self.acad.model.AddBox(APoint(right_wall_center), rw['length'], rw['width'], rw['height'])
                right_wall.Color = 5
                rw['vol'] = str(right_wall.Volume)
                rw['centroid'] = right_wall.Centroid
                self.model.append(rw)
            elif key == 'fw':
                # Add front wall
                fw = value
                front_wall_center = (fw['length'] / 2 + self.geometry['lw']['length'], fw['width'] / 2, fw['height'] / 2 + bs['height'])
                front_wall = self.acad.model.AddBox(APoint(front_wall_center), fw['length'], fw['width'], fw['height'])
                front_wall.Color = 6
                fw['vol'] = str(front_wall.Volume)
                fw['centroid'] = front_wall.Centroid
                self.model.append(fw)
            elif key == 'wed_fw':
                # Add wedge front wall
                wed_fw = value
                front_wall_center = (
                fw['length'] / 2 + lw['length'], fw['width'] / 2, fw['height'] + bs['height'] + wed_fw['height'] / 2)
                wed_front = self.acad.model.AddWedge(APoint(front_wall_center), -fw['length'], fw['width'],
                                                     wed_fw['height'])
                wed_front.Color = 6
                wed_fw['vol'] = str(wed_front.Volume)
                wed_fw['centroid'] = wed_front.Centroid
                self.model.append(wed_fw)
            elif key == 'bw':
                # Add back wall
                bw = value
                back_wall_center = (
                bw['length'] / 2 + self.geometry['lw']['length'], bs['width'] - bw['width'] / 2, bw['height'] / 2 + bs['height'])
                back_wall = self.acad.model.AddBox(APoint(back_wall_center), bw['length'], bw['width'], bw['height'])
                back_wall.Color = 6
                bw['vol'] = str(back_wall.Volume)
                bw['centroid'] = back_wall.Centroid
                self.model.append(bw)
            elif key == 'wed_bw':
                # Add wedge back wall
                wed_bw = value
                back_wall_center = (bw['length'] / 2 + lw['length'], bs['width'] - bw['width'] / 2,
                                    bw['height'] + bs['height'] + wed_bw['height'] / 2)
                wed_back = self.acad.model.AddWedge(APoint(back_wall_center), -bw['length'], bw['width'],
                                                    wed_bw['height'])
                wed_back.Color = 6
                wed_bw['vol'] = str(wed_back.Volume)
                wed_bw['centroid'] = wed_back.Centroid
                self.model.append(wed_bw)
            elif key == 'int_beam_1':
                # Add interior beam 1
                int_beam_1 = value
                beam_1_center = (int_beam_1['length']/2 + 2 + 16/12, 2/3 * (16.667 - 32/12) + 16/12, int_beam_1['height']/2 + bs['height'])
                beam_1 = self.acad.model.AddBox(APoint(beam_1_center), int_beam_1['length'], int_beam_1['width'], int_beam_1['height'])
                int_beam_1['vol'] = str(beam_1.Volume)
                int_beam_1['centroid'] = beam_1.Centroid
                self.model.append(int_beam_1)
            elif key == 'int_beam_2':
                # Add interior beam 2
                int_beam_2 = value
                beam_2_center = (int_beam_2['length']/2 + 2 + 16/12, 1/3 * (16.667 - 32/12) + 16/12, int_beam_2['height']/2 + bs['height'])
                beam_2 = self.acad.model.AddBox(APoint(beam_2_center), int_beam_2['length'], int_beam_2['width'], int_beam_2['height'])
                int_beam_2['vol'] = str(beam_2.Volume)
                int_beam_2['centroid'] = beam_2.Centroid
                self.model.append(int_beam_2)
            elif key == 'leg1':
                # Add leg1
                leg1 = value
                leg_1_center = (leg1['length'] / 2 + 6, leg1['width'] / 2, 0 - leg1['height'] / 2)
                leg_1 = self.acad.model.AddBox(APoint(leg_1_center), leg1['length'], leg1['width'], leg1['height'])
                leg_1.Color = 11
                leg1['vol'] = str(leg_1.Volume)
                leg1['centroid'] = leg_1.Centroid
                # self.model.append(leg1)
            elif key == 'leg2':
                # Add leg2
                leg2 = value
                leg_2_center = (
                leg2['length'] / 2 + leg1['length'] + 83 / 12 + 6, leg2['width'] / 2, 0 - leg2['height'] / 2)
                leg_2 = self.acad.model.AddBox(APoint(leg_2_center), leg2['length'], leg2['width'], leg2['height'])
                leg_2.Color = 11
                leg2['vol'] = str(leg_2.Volume)
                leg2['centroid'] = leg_2.Centroid
                # self.model.append(leg2)

        # Add forces
        # Add Active loading
        act_center = (bs['length'] + 2, rw['width']/2, (rw['height'] + bs['height'])/2)
        act_force = self.acad.model.AddWedge(APoint(act_center), 2, rw['width'], (rw['height'] + bs['height']))
        act_force.Color = 1

        # Add EQ loading
        eq_center = (bs['length'] + 5, rw['width']/2, (rw['height'] + bs['height'])/2)
        eq_force = self.acad.model.AddWedge(APoint(eq_center), 2, rw['width'], -(rw['height'] + bs['height']))
        eq_force.Color = 2

        # self.model = [bs, lw, rw, fw, wed_fw, bw, wed_bw, ts]
        # self.model = [bs, lw, rw, fw, bw, int_beam_1, int_beam_2, ts]

    def analyze(self):

        # get data from model created
        # for obj in self.model:
        #     print(f'ID: {obj["id"]}, vol: {obj["vol"]}, centroid: {obj["centroid"]}')

        # set pivot point
        # Cylinder: (Center, Radius, Height)
        # self.acad.regen = True
        rad = 0.3
        cyl = self.acad.model.AddCylinder(APoint(0, rad, self.max_width/2), rad, self.max_width)
        cyl.Rotate3D(APoint(0, 0, 0), APoint(5, 0, 0), -math.pi/2)
        # self.acad.regen = True
        # self.acad.app.ZoomExtents()

        print(self.model)

        # get weights
        for obj in self.model:
            print(obj)


        # calculate weights, moment arms, moments
        for i in range(len(self.model)):
            self.model[i]['weight'] = float(self.model[i]['vol']) * float(self.prop['g_conc'])    # ans in lbs
            self.model[i]['arm'] = float((self.model[i]['centroid'])[0]) - 0    # x perpendicular
            self.model[i]['weight_moment'] = float(self.model[i]['weight']) * float(self.model[i]['arm'])

        # calculate seismic inertia, moment arms, moments
        for i in range(len(self.model)):
            self.model[i]['seismic_inertia'] = float(self.model[i]['weight']) * float(self.prop['pga_eff']) # ans in lbs
            self.model[i]['arm'] = float(self.model[i]['centroid'][2]) - 0    # z perpendicular
            self.model[i]['seis_inertia_moment'] = float(self.model[i]['seismic_inertia']) * float(self.model[i]['arm']) * -1 # overturning moment

        # add seismic, active, passive forces
        active = {
            'id': 'active force',
            'force': 0.5 * float(self.prop['g_active']) * float(self.prop['g_active_height']) ** 2 * float(self.prop['soil_width']) * -1,
            'arm': 1/3 * float(self.prop['g_active_height'])
        }
        eq = {
            'id': 'eq force',
            'force': 0.5 * float(self.prop['g_eq']) * float(self.prop['g_eq_height']) ** 2 * float(self.prop['soil_width']) * -1,
            'arm': 2/3 * float(self.prop['g_eq_height'])
        }
        passive = {
            'id': 'passive force',
            'force': 0.5 * float(self.prop['g_passive']) * float(self.prop['g_passive_height']) ** 2 * float(self.prop['soil_width']),
            'arm': 2/3 * float(self.prop['g_passive_height'])
        }

        self.soil_forces = [active, eq, passive]
        for i in range(len(self.soil_forces)):
            self.soil_forces[i]['moment'] = float(self.soil_forces[i]['force']) * float(self.soil_forces[i]['arm'])

        for obj in self.model:
            self.resisting = self.resisting + obj['weight_moment']
            self.seismic_inertia_moment = self.seismic_inertia_moment + obj['seis_inertia_moment']

        self.resisting = self.resisting + self.soil_forces[2]['moment']

        print(f'Resisting: {round(self.resisting/1000, 2)} kip-ft')
        print(f'Seismic Inertia: {round(self.seismic_inertia_moment/1000, 2)} kip-ft')

        for a in self.soil_forces:
            print(f'{a["id"].title()}: {round(a["moment"]/1000, 2)} kip-ft')

        self.overturning = self.soil_forces[0]['moment'] + self.soil_forces[1]['moment'] + self.seismic_inertia_moment
        print(f'Overturning: {self.overturning} kip-ft\nResisting: {self.resisting} kip-ft\nFactor of safety: {abs(self.resisting/self.overturning)}')
        # print(self.overturning)


        # for obj in self.model:
        #     print(obj)

        return self.model


g_soil = 90
ka = 0.3
kp = 3.1
keq = 0.5

properties = {
    'g_conc': 150,  # pcf
    'pga_eff': 2/3 * 0.3,   # pga
    'g_active': 40.56,          # pcf
    'g_eq': 92.04,             # pcf
    'g_passive': 786.24,       # pcf
    'g_active_height': 9,   # ft
    'g_eq_height': 9,       # ft
    'g_passive_height': 4,  # ft
    'soil_width': 16.67
}


camanche_valve_house = {
    # Add Base
    'bs': {
        'id': 'base slab',
        'height': 0.5,
        'width': 73,
        'length': 15,
    },
    'ts': {
        'id': 'top slab',
        'height': 0.5,
        'length': 15,
        'width': 73,
        'angle': atan(1 / 15) * -1
    },
    'fw': {
        'id': 'front wall',
        'height': 8,
        'width': 0.5,
        'length': 14
    },
    'bw': {
        'id': 'back wall',
        'height': 8,
        'width': 0.5,
        'length': 14
    },
    'lw': {
        'id': 'left wall',
        'height': 8,
        'width': 73,
        'length': 0.5
    },
    'rw': {
        'id': 'right wall',
        'height': 9,
        'width': 73,
        'length': 0.5
    },
    'wed_fw': {
        'id': 'wedge front wall',
        'height': 1,
        'width': 0.5,
        'length': 14,
        'include': True
    },
    'wed_bw': {
        'id': 'wedge back wall',
        'height': 1,
        'width': 0.5,
        'length': 14,
        'include': True
    },
    'leg1': {
        'id': 'leg 1',
        'height': 104 / 12,
        'width': 73,
        'length': 1,
    },
    'leg2': {
        'id': 'leg 2',
        'height': 104 / 12,
        'width': 73,
        'length': 1,
    },
}

seepage_monitoring_vault = {
    # Add Base
    'bs': {
        'id': 'base slab',
        'height': 1.5,
        'length': 10.667,
        'width': 16.667
    },

    'ts': {
        'id': 'top slab',
        'height': 0.5,
        'length': 10.667,
        'width': 16.667,
    },

    'fw': {
        'id': 'front wall',
        'height': 9,
        'width': 16 / 12,
        'length': 10.667 - 32 / 12
    },
    'bw': {
        'id': 'back wall',
        'height': 9,
        'width': 16 / 12,
        'length': 10.667 - 32 / 12
    },
    'lw': {
        'id': 'left wall',
        'height': 9,
        'width': 16.667,
        'length': 16 / 12
    },
    'rw': {
        'id': 'right wall',
        'height': 9,
        'width': 16.667,
        'length': 16 / 12
    },

    'int_beam_1': {
        'id': 'int beam 1',
        'height': 2,
        'width': 2,
        'length': 10.667 - 2 - 32 / 16,
    },

    'int_beam_2': {
        'id': 'int beam 2',
        'height': 2,
        'width': 2,
        'length': 10.667 - 2 - 32 / 16,
    },
}



res = Model(model=camanche_valve_house, prop=properties).analyze()
print(res)
print(f'Objects found: {len(res)}')
