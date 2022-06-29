from opentrons import protocol_api
import math

#import json
#with open('C:/Users/ferna/AppData/Roaming/Opentrons/labware/Greiner Bio-One 96 Well Plate Half-Area 175 uL.json') as labware_file:
#    greinerbioone_96_wellplate_175ul = json.load(labware_file)

metadata = {
    'apiLevel' : '2.9',
    'protocolName': 'ELISA ASSAY PREP -- PRIMARY ANTIBODY',
    'author': 'Fernan Aguero <fernan@iib.unsam.edu.ar>',
    'source': 'Trypanosomatics Lab -- Custom Protocol'
}

# EXPLANATION 
# The idea of this protocol is to assay each antigen in duplicate.
# Because plates already have antigens bound to wells in 4 replicates
# we will use two replicates for 1 serum sample and the remaining replicates for another serum sample
# 8 wells in each plate are assayed with positive and negative controls
#                                            6 Ags x 4
#                                           ----------
#                               8 Ags x 4   |  |  |  |
#                               ----------  |  |  |  |
#                   8 Ags x 4   |  |  |  |  |  |  |  |
#                   ----------  |  |  |  |  |  |  |  |
#                   |  |  |  |  |  |  |  |  |  |  |  |
# ELISA Columns:    01 02 03 04 05 06 07 08 09 10 11 12
#                  ------------------------------------  
#       Rows:   A | S1 S1 S2 S2 S1 S1 S2 S2 S1 S1 S2 S2
#               B | S1 S1 S2 S2 S1 S1 S2 S2 S1 S1 S2 S2
#               C | S1 S1 S2 S2 S1 S1 S2 S2 S1 S1 S2 S2
#               D | S1 S1 S2 S2 S1 S1 S2 S2 S1 S1 S2 S2
#               E | S1 S1 S2 S2 S1 S1 S2 S2 S1 S1 S2 S2
#               F | S1 S1 S2 S2 S1 S1 S2 S2 S1 S1 S2 S2
#               G | S1 S1 S2 S2 S1 S1 S2 S2 CS CS CS CS <- CS = control serum 
#               H | S1 S1 S2 S2 S1 S1 S2 S2 CS CS CS CS <- CS = control serum 
#                                         ^  ^  ^  ^
#                                         |  |  |  |

# OPENTRONS TUBE RACK SAMPLE LAYOUT
# ELISA Columns:     01  02  03  04  05  06 
#                  -------------------------  
#       Rows:   A |  S1  S2  S3  S4  S5  S6
#               B |  S7  S8  S9 S10 S11 S12
#               C | S13 S14 S15 S16  --  --
#               D |  --  --  --  --  CS  CS

         
# REQUIRES
# TIPRACK 300 ul with at least 3 complete columns with tips in SLOT 11
# SINGLE p300 PIPETTE mounted on the RIGHT side OF OT-2 arm 
# ELISA PLATES (Greiner Bio-One 96well Half-Area) in SLOTS 1-8
# OPENTRONS TUBE RACK with 2mL Eppendorf tubes in SLOT 10 
#   with tubes in positions A1 through C4 (16 tubes) containing 1.2mL primary Ab 
#   and tubes in positions D5 and D6 containing 0.9 mL of control Ab (each one)
#   both already prepared at the working dilution 
# the protocol will dispense three primary Abs (2 experimental + 1 control) per plate 
# as per the map above (see also plate_sera_map in the code)

# IMPORTANT
# the volumes in tubes must be those specified above and below (1.1 mL  and 0.8 mL) + safe volume (0.075-0.1 mL)
# this is because we keep track of remaining volume to adjust the height/depth
# of the pipetting process at each step. 



# define initial height settings
# this is ONLY valid for Eppendorf 1.5 mL tubes!!!
source_tube_v_height = 17.8 # height of the conical (V-shaped bottom) section of the tube, in milimeters

source_tube_c_radius = 4.35 # radius of the cylindrical (middle) section of the tube, in milimeters
immersion_depth = 6 # default immersion of the tip into the liquid, in milimeters

# JUST BEFORE RUNNING THE PROTOCOL|
# Prepare dilution of antigens in binding buffer at the desired concentration
# and place 1mL of each antigen in wells A1 through H3 (3 columns, 24 wells)

# BOTTOM CLEARANCE FUNCTION
def calc_bottom_clearance (height, remaining_volume, radius, immersion_depth):
    "Return the calculated bottom clearance with 1 decimal precision"
    the_bottom_clearance = height + (remaining_volume / (math.pi * (math.pow(radius,2))) ) - immersion_depth 
    rbc = round(the_bottom_clearance,1)
    return rbc

# START our opentrons protocol
# This protocol takes about 35 minutes (last update 3/8/2021)
def run(protocol: protocol_api.ProtocolContext):
    # logic for liquid adjustment level is explained in the 
    # LIQUID-LEVEL-ADJUSTMENT-NOTES.md file in the repo
    # we subtract the volume of the conical section of the tube
    # because we only care for calculation in the cylindrical section
    initial_volume_experimental_antibodies = 1200 - 500 
    initial_volume_control_antibodies = 900 - 500 
    bottom_clearance_default = 1.2
    # and there are two tubes with CS = control serum
    control_serum_d5_remaining_volume = initial_volume_control_antibodies
    control_serum_d6_remaining_volume = initial_volume_control_antibodies
    # LOAD tips and pipette
    tiprack_11 = protocol.load_labware('opentrons_96_tiprack_300ul', '10')
    pipette_single = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_11])
    #pipette_multi = protocol.load_instrument('p300_multi', 'left', tip_racks=[tiprack_11])
    # LOAD the tube rack containing the serum samples
    stock_plate = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '11')
    # maybe also try opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap

    # LOAD our ELISA plates (8)
    elisa_plates=[]
    for plate in range(1,9,1):
        elisa_plates.append(protocol.load_labware('greinerbioone_96_wellplate_175ul', plate, label="ELISA Plate {}".format(plate)))

    # here we create a hash/dict with source wells/locations for each serum
    plate_sera_map = {
        'plate1': { 'serum1': 'A1', 'serum2': 'A2' },
        'plate2': { 'serum1': 'A3', 'serum2': 'A4' },
        'plate3': { 'serum1': 'A5', 'serum2': 'A6' },
        'plate4': { 'serum1': 'B1', 'serum2': 'B2' },
        'plate5': { 'serum1': 'B3', 'serum2': 'B4' },
        'plate6': { 'serum1': 'B5', 'serum2': 'B6' },
        'plate7': { 'serum1': 'C1', 'serum2': 'C2' },
        'plate8': { 'serum1': 'C3', 'serum2': 'C4' }
    }

    # here we create a hash/dict to track remaining volume and pipetting height for each tube
    height_volume_dict = {
        'A1': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'A2': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'A3': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'A4': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'A5': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'A6': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'B1': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'B2': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'B3': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'B4': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'B5': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'B6': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'C1': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'C2': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'C3': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'C4': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_experimental_antibodies},
        'D5': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_control_antibodies},
        'D6': { 'height': source_tube_v_height, 'remaining_volume': initial_volume_control_antibodies}
    }

    # here we create a hash/dict with destination wells/locations for each sera
    plate_dest_map = { 
        'serum1': [],
        'serum2': [],
        'control_serum': []
    }
    for column in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
        # block of colums for serum 1 
        for row in ['1', '2', '5', '6', '9', '10']:
            well = column + row
            if well not in ['G9', 'G10', 'H9', 'H10']:
                plate_dest_map['serum1'].append(well)
            else:
                plate_dest_map['control_serum'].append(well)
        # block of columns for serum2
        for row in ['3', '4', '7', '8', '11', '12']:
            well = column + row
            if well not in ['G11', 'G12', 'H11', 'H12']:
                plate_dest_map['serum2'].append(well)
            else:
                plate_dest_map['control_serum'].append(well)
    
    # we will now iterate platewise and within plates serumwise 
    # so we use a single tip for all assays with the same serum sample
    plate_count=1
    control_serum = 'D5'
    for plate in elisa_plates:
        for serum in ['1', '2']:
            # initialize values for all things we need to track
            serum_source_well = plate_sera_map['plate{}'.format(plate_count)]['serum{}'.format(serum)]
            serum_source_remaining_volume = initial_volume_experimental_antibodies
            source_tube = stock_plate.wells_by_name()[serum_source_well]
            
            # calculate initial bottom clearance for pipetting (immersion/height) given remaining volume in source tube
            bottom_clearance = calc_bottom_clearance(source_tube_v_height,initial_volume_experimental_antibodies,source_tube_c_radius,immersion_depth)
            aspiration_rate = 1
            protocol.comment("DEBUG: initial bottom clearance = {}".format(bottom_clearance))
            effective_remaining_vol = serum_source_remaining_volume + 500
            protocol.comment("DEBUG: initial remaining volume = {}".format(effective_remaining_vol))
            # set initial bottom clearance for aspiration operations
            #pipette_single.well_bottom_clearance.aspirate = 3
            
            # pick up tip
            pipette_single.pick_up_tip()
            count = 0
            ncount = 0
            # first time we aspirate an extra 50 ul which will be our safety / disposal volume
            #pipette_single.aspirate(250,source_tube)
            pipette_single.aspirate(250,source_tube.bottom(bottom_clearance),rate = aspiration_rate)
            # and we update the remaining volume in the tube
            serum_source_remaining_volume -= 250
            # and the bottom clearance
            bottom_clearance = calc_bottom_clearance(source_tube_v_height,serum_source_remaining_volume,source_tube_c_radius,immersion_depth)
            protocol.comment("DEBUG: updated bottom clearance = {}".format(bottom_clearance))
            effective_remaining_vol = serum_source_remaining_volume + 500
            protocol.comment("DEBUG: updated remaining volume = {}".format(effective_remaining_vol))
            # then we keep aspirating what we dispense
            aspirationvolume=200
            dispensevolume=25
            for well in plate_dest_map['serum{}'.format(serum)]:
                if ncount == 4:
                    aspirationvolume = 100
                if count == 8:
                    pipette_single.aspirate(aspirationvolume,stock_plate.wells_by_name()[serum_source_well].bottom(bottom_clearance),rate = aspiration_rate)
                    ncount += 1
                    serum_source_remaining_volume -= aspirationvolume
                    if effective_remaining_vol > 500:
                        bottom_clearance = calc_bottom_clearance(source_tube_v_height,serum_source_remaining_volume,source_tube_c_radius,immersion_depth)
                        aspiration_rate = 1
                    else:
                        bottom_clearance = bottom_clearance_default # at this clearance there is no risk of spill over if tip goes too down
                        aspiration_rate = 0.4
                    protocol.comment("DEBUG: updated bottom clearance = {}".format(bottom_clearance))
                    effective_remaining_vol = serum_source_remaining_volume + 500
                    protocol.comment("DEBUG: updated remaining volume = {}".format(effective_remaining_vol))
                    count = 0
                pipette_single.dispense(dispensevolume,plate.wells_by_name()[well])
                count += 1
            # when we finish this block we blow out the safety volume back to the source
            pipette_single.blow_out(stock_plate.wells_by_name()[serum_source_well])
            # dispose the tips
            pipette_single.drop_tip()
        # now we dispense control serum in G9:H12
        # there are two tubes with CS = control serum
        #global control_serum_d5_remaining_volume
        #global control_serum_d6_remaining_volume
        d5_remaining_volume = control_serum_d5_remaining_volume
        d6_remaining_volume = control_serum_d6_remaining_volume
        effective_d5_remaining_vol = d5_remaining_volume + 500
        effective_d6_remaining_vol = d6_remaining_volume + 500
        
        # calculate initial bottom clearance for pipetting (immersion/height) given remaining volume in source tube
        if control_serum == 'D5':
            if effective_d5_remaining_vol > 500:
                bottom_clearance = calc_bottom_clearance(source_tube_v_height,d5_remaining_volume,source_tube_c_radius,immersion_depth)
                aspiration_rate = 1
            else:
                bottom_clearance = bottom_clearance_default # at this clearance there is no risk of spill over if tip goes too down
                aspiration_rate = 0.4                
        else: 
            d6_remaining_volume -= 250
            if effective_d6_remaining_vol > 500:
                bottom_clearance = calc_bottom_clearance(source_tube_v_height,d6_remaining_volume,source_tube_c_radius,immersion_depth)
                aspiration_rate = 1
            else:
                bottom_clearance = bottom_clearance_default # at this clearance there is no risk of spill over if tip goes too down
                aspiration_rate = 0.4  

            
        protocol.comment("DEBUG: initial bottom clearance for control serum = {}".format(bottom_clearance))
        effective_d5_remaining_vol = d5_remaining_volume + 500
        effective_d6_remaining_vol = d6_remaining_volume + 500
        protocol.comment("DEBUG: initial remaining volume for d5 control serum = {}".format(effective_d5_remaining_vol))
        protocol.comment("DEBUG: initial remaining volume for d6 control serum = {}".format(effective_d6_remaining_vol))
        # set initial bottom clearance for aspiration operationseffective_d5_remaining_vol        pipette_single.well_bottom_clearance.aspirate = bottom_clearance
        pipette_single.pick_up_tip()
        ccount = 0
        # first time we aspirate an extra 50 ul which will be our safety / disposal volume
        
        pipette_single.aspirate(250,stock_plate.wells_by_name()[control_serum].bottom(bottom_clearance),rate = aspiration_rate)
        # and we update the remaining volume in the tube and the bottom clearance
        if control_serum == 'D5':
            d5_remaining_volume -= 250
            if effective_d5_remaining_vol > 500:
                bottom_clearance = calc_bottom_clearance(source_tube_v_height,d5_remaining_volume,source_tube_c_radius,immersion_depth)
            else:
                bottom_clearance = bottom_clearance_default # at this clearance there is no risk of spill over if tip goes too down
                aspiration_rate = 0.4                
        else: 
            if effective_d6_remaining_vol > 500:
                bottom_clearance = calc_bottom_clearance(source_tube_v_height,d6_remaining_volume,source_tube_c_radius,immersion_depth)
            else:
                bottom_clearance = bottom_clearance_default # at this clearance there is no risk of spill over if tip goes too down
                aspiration_rate = 0.4                  
        protocol.comment("DEBUG: updated bottom clearance = {}".format(bottom_clearance))
        effective_d5_remaining_vol = d5_remaining_volume + 500
        effective_d6_remaining_vol = d6_remaining_volume + 500
        protocol.comment("DEBUG: update remaining volume for d5 control serum = {}".format(effective_d5_remaining_vol))
        protocol.comment("DEBUG: update remaining volume for d6 control serum = {}".format(effective_d6_remaining_vol))
        # then we keep aspirating what we dispense
        aspirationvolume=200
        dispensevolume=25
        for cwell in plate_dest_map['control_serum']:
            if ccount == 8:
                pipette_single.aspirate(aspirationvolume,stock_plate.wells_by_name()[control_serum].bottom(bottom_clearance),rate = aspiration_rate)
                # and we update the remaining volume in the tube and the bottom clearance
                if control_serum == 'D5':
                    d5_remaining_volume -= aspirationvolume
                    if effective_d5_remaining_vol > 500:
                        bottom_clearance = calc_bottom_clearance(source_tube_v_height,d5_remaining_volume,source_tube_c_radius,immersion_depth)
                    else: 
                        protocol.commet("Using default bottom clearance")
                        bottom_clearance = bottom_clearance_default # at this clearance there is no risk of spill over if tip goes too down
                        aspiration_rate = 0.4
                else: 
                    d6_remaining_volume -= aspirationvolume
                    if effective_d6_remaining_vol > 500:
                        bottom_clearance = calc_bottom_clearance(source_tube_v_height,d6_remaining_volume,source_tube_c_radius,immersion_depth)
                        aspiration_rate = 1
                    else:
                        protocol.commet("Using default bottom clearance")
                        bottom_clearance = bottom_clearance_default # at this clearance there is no risk of spill over if tip goes too down
                        aspiration_rate = 0.4
                protocol.comment("DEBUG: updated bottom clearance = {}".format(bottom_clearance))
                effective_d5_remaining_vol = d5_remaining_volume + 500
                effective_d6_remaining_vol = d6_remaining_volume + 500
                protocol.comment("DEBUG: update remaining volume for d5 control serum = {}".format(effective_d5_remaining_vol))
                protocol.comment("DEBUG: update remaining volume for d6 control serum = {}".format(effective_d6_remaining_vol))
                ccount = 0
            pipette_single.dispense(dispensevolume,plate.wells_by_name()[cwell])
            ccount += 1
        if plate_count == 4:
            pipette_single.blow_out(stock_plate.wells_by_name()[control_serum])
            control_serum = 'D6'
        else: 
            pipette_single.blow_out(stock_plate.wells_by_name()[control_serum])
        
        if control_serum == 'D5':
            d5_remaining_volume += 50
        else:
            d6_remaining_volume += 50
        # update the remaining volume of the control serum 
        if control_serum == 'D5':
            control_serum_d5_remaining_volume = d5_remaining_volume
        else: 
            control_serum_d6_remaining_volume = d6_remaining_volume
        # when we finish this block we blow out the safety volume back to the source

        # dispose the tips
        pipette_single.drop_tip()
        plate_count += 1



        # NOTES ON VOLUME 
        # Eppendorf tube measures taken from technical drawings
        # https://www.eppendorf.com/product-media/doc/en/140027_Technical-Data/Eppendorf_Consumables_Technical-data_Safe-Lock-Tube-15-mL_Safe-Lock-15-mL-technical-drawing.pdf
        # linear  section 1 -- from top to 0.5 mL mark when it starts to be conical (V shaped bottom)
        # conical section 2 -- from 0.5 mL mark down to bottom (V shaped)
        # top to start of liquid = 2 mm
        # height from top to bottom (inside tube) = 37.8 mm
        # height of section 1 = 20 mm
        # effective / recommended volume of section 1 = 1000 mm3 = 1 mL
        # effective / recommended filling height of section 1 = 16.82 mm
        # diameter of section 1 = 8.7 mm; radius = 4.35 mm
        # height of section 2 = 17.8 mm
        # volume of section 2 = 500 mm3 = 0.5 mL
        # diameter of section 2 goes from 8.7 mm at top to 3.6 mm at bottom
        # volume = pi * (radius^2) * height
        # height = volume / pi * (radius^2)
        # https://www.calculatorsoup.com/calculators/geometry-solids/cylinder.php
        # e.g. the height of 50 uL in section 1 is: 50 mm3 / 3.141592 * (4.35^2) = 0.841088 mm
        # 250 ul / 3.141592 * (4.35^2) = 4.2 mm
        # DRAFT LOGIC - immersion_depth = 3 - 0.7 mm as per this eppendorf guide 
        # https://www.eppendorf.com/product-media/doc/en/109136_Userguide/Eppendorf_Automated-Liquid-Handling_Userguide_005_epMotion-5070_5075_Minimization-remaining-volumes-plates-tubes.pdf
        # if remaining_volume > 0.5:
        #   bottom_clearance = 17.8 + (remaining_volume / 3.141592 * (4.35^2)) - immersion_depth
        # else: 
        #   bottom_clearance = 1.7 # at this clearance there is no risk of spill over if tip goes too down
        


