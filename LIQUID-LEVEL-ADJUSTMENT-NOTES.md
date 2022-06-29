# VOLUME MANAGEMENT ON OPENTRONS PROTOCOLS

In opentrons protocols, if we use tubes holding large volumes (15 or 50 mL tubes) to distribute to a lot of wells, with the default pipetting settings, the pipette always goes to ~ 1 mm from bottom of the tube, even if the tube is full. This means that the pipette itself, not just the tip, may come in contact with the liquid. This is of course a problem and can cause contamination.

As an example, if you run a protocol along the lines of the following, the pipette will go to the very bottom of the 15ml tube in well A1. If that tube was full, it would spill. Even if it is not full, in the case of deep tubes the liquid will touch the pipette itself.

````
tiprack = protocol.load_labware('opentrons_96_tiprack_300ul', '1')
pipette = protocol.load_instrument('p300_single', 'right')
tubes = protocol.load_labware('opentrons_15_tuberack_falcon_15ml_conical', 3)
pipette.pick_up_tip()
pipette.aspirate(200, tubes.wells('A1')
pipette.dispense(tubes.wells('A2')
````

The same problem may happen as well with smaller tubes (1.5 or 2 mL Eppendorf tubes, or when using deep wells in plates), if the tubes contain liquid up to their max capacity. 

One possible solution relies on being able to tell a particular labware how much liquid there is in the tube, and then perform volume and height calculations to determine and adjust the pipetting depth, which would be different from the well depth.

# EXAMPLE WITH EPPENDORF TUBES

Eppendorf tube measures were taken from [Eppendorf technical drawings](https://www.eppendorf.com/product-media/doc/en/140027_Technical-Data/Eppendorf_Consumables_Technical-data_Safe-Lock-Tube-15-mL_Safe-Lock-15-mL-technical-drawing.pdf).

According to these drawings these are some guide measurements and volume calculations, along with some code ideas to adjust pipetting depth and remaining volume. 

````
cylindrical section 1 -- from top to 0.5 mL mark (just when it starts to be conical)
conical section 2 -- from 0.5 mL mark down to bottom (V shaped)
top of tube to start of liquid = 2 mm
height from top to bottom (inside tube) = 37.8 mm
height of section 1 = 20 mm
effective / recommended volume of section 1 = 1000 mm3 = 1 mL
effective / recommended filling height of section 1 = 16.8218 mm
diameter of section 1 = 8.7 mm; radius = 4.35 mm
height of section 2 = 17.8 mm
volume of section 2 = 500 mm3 = 0.5 mL
diameter of section 2 goes from 8.7 mm at top to 3.6 mm at bottom
volume = pi * (radius^2) * height
height = volume / pi * (radius^2)
e.g. the height of 50 uL in section 1 is: 50 mm3 / 3.141592 * (4.35^2) = 0.841088 mm
e.g. the volume of section 1 is: 3.141592 * (4.35 mm ^2) * 16.8218 mm = 1000 mm3
````

# DRAFT LOGIC FOR 1.5 mL EPPENDORF TUBES

When discussing the recommended immersion tip depth, the Eppendorf guides for their robots mention that the immersion_depth is usually 3 mm. We also know that in Opentrons as well, there is always a 1 mm clearance from the bottom of the tube. Hence, we could use these values in the following logic (untested):

````
immersion_depth = 3
height_of_conical_section = 17.8
if remaining_volume > 0.5:  # we are in the cylindrical section 1 of the tube, hence we can calculate height given a volume
  bottom_clearance = height_of_conical_section + (remaining_volume / 3.141592 * (4.35^2)) - immersion_depth
else: 
  bottom_clearance = 1.7 # at this clearance there is no risk of spill over if tip goes too down
# Aspirate using the calculated bottom clearance
pipette.well_bottom_clearance.aspirate = bottom_clearance
pipette.aspirate(volume, tube['A1'])
````

# WORKING WITH OTHER TUBES

The same logic applies to other tubes, e.g. Falcon 15 and 50 mL tubes. Using the technical drawings it is easy to identify the cylindrical section of each tube and obtain the corresponding radius and height of this section as well as the height of the conical (V-shaped) bottom section. For example see files "16871 15 mL Falcon Graduated Tubes Data Sheet", and "16871 50 mL Falcon Graduated Tubes Data Sheet".

# REFERENCES

 1 [Eppendorf technical drawings - 1.5 mL Tube](https://www.eppendorf.com/product-media/doc/en/140027_Technical-Data/Eppendorf_Consumables_Technical-data_Safe-Lock-Tube-15-mL_Safe-Lock-15-mL-technical-drawing.pdf)
 
 2 [Eppendorf technical drawings - 2.0 mL Tube](https://www.eppendorf.com/product-media/doc/en/140034_Technical-Data/Eppendorf_Consumables_Technical-data_Safe-Lock-Tube-20-mL_Safe-Lock-20-ml-technical-drawing.pdf)

 3 [Eppendorf Minimization of Remaining Volumes in Plates and Tubes](https://www.eppendorf.com/product-media/doc/en/109136_Userguide/Eppendorf_Automated-Liquid-Handling_Userguide_005_epMotion-5070_5075_Minimization-remaining-volumes-plates-tubes.pdf)
 
 4 [Cylinder Volume Calculator](https://www.calculatorsoup.com/calculators/geometry-solids/cylinder.php)