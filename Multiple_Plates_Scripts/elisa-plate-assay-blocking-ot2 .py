from opentrons import protocol_api

#import json
#with open('C:/Users/ferna/AppData/Roaming/Opentrons/labware/Greiner Bio-One 96 Well Plate Half-Area 175 uL.json') as labware_file:
#    greinerbioone_96_wellplate_175ul = json.load(labware_file)

metadata = {
    'apiLevel' : '2.4',
    'protocolName': 'ELISA ASSAY PREP -- Blocking',
    'author': 'Bracco Leonel - Fernan Aguero <fernan@iib.unsam.edu.ar>',
    'source': 'Trypanosomatics Lab -- Custom Protocol'
}

# EXPLANATION 
# The idea of this protocol is to dispense blocking solution in all plates (TBS with 5% milk). 
# This script is very simple and will dispense blocking solution in all wells for all 8 plates



# REQUIRES
# TIPRACK 300 ul with column 1 complete with tips in SLOT 11
# MULTI p300 PIPETTE mounted on the LEFT side OF OT-2 arm 
# ELISA PLATES (Greiner Bio-One 96well Half-Area) in SLOTS 1-8
# NEST 1 reservoir (195 mL) in SLOT 10 
# filled with blocking solution at the working dilution 
# the protocol uses 9.6 mL for each plate (76.8 mL for 8)
# so we need an extra volume in each reservoir to account for bed volume for pipetting and reservoir leftover (about 95 mL total is fine)

# JUST BEFORE RUNNING THE PROTOCOL
# Prepare blocking ddilution TBS + 5% non-fat dry milk (NFDM)
# e.g. for 90 ml, mix 90 ml TBS and 4.5 g NFDM

# START our opentrons protocol
# This protocol takes about 10 minutes (last checked 3/8/2021) (Gen 2 pippete)

reservoir_column = 'A1'
def run(protocol: protocol_api.ProtocolContext):

    # SET PLATES TO RUN:----------------------------------------------------------------------------------------------------------------------------------------------------
    number_plates = 5
    pipette = 300
    pipette_position = "left"    
    dispensevolume = 100
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    

    # LOAD tips and pipette
    tiprack_11 = protocol.load_labware('opentrons_96_tiprack_300ul', '10')
    if (pipette == 50):
        pipette_multi = protocol.load_instrument('p50_multi', pipette_position, tip_racks=[tiprack_11])
    if (pipette == 300):
        pipette_multi = protocol.load_instrument('p300_multi', pipette_position, tip_racks=[tiprack_11])
    # LOAD the reservoir containing the blocking solution
    stock_reservoir = protocol.load_labware('nest_1_reservoir_195ml', '11')
    reservoirTotalVolume = 195000 #volume in ul taken from manual

    deadVolume = 13200
    reservoirInitialFill = deadVolume + 96 * dispensevolume * number_plates
    protocol.comment("CONTROL: Reservoir NEST 1 reservoir (195 mL) containing: {}".format(reservoirInitialFill)+"ul")
    reservoirFill = reservoirInitialFill
    depth = 25 #depth in mm taken from manual
    aspirationHigh = reservoirFill / reservoirTotalVolume * depth
    if (pipette == 50):
        aspirationvolume=50
    if (pipette == 300):
        aspirationvolume=200
    bottomCleareance = 3
    # LOAD our ELISA plates (8) 
    elisa_plates=[]
    for plate in range(1,(number_plates+1),1):
        elisa_plates.append(protocol.load_labware('greinerbioone_96_wellplate_175ul', plate, label="ELISA Plate {}".format(plate)))

        
    pipette_multi.pick_up_tip()
    aspiration_count = 0
    for plate in elisa_plates:
        aspirated = aspirationvolume
        if (pipette >= 50 + dispensevolume):
            safeVolume = 50
        else:
            safeVolume = 0
        aspirationRate = 0.2 + reservoirFill / reservoirInitialFill * 0.8
        if aspirationHigh < bottomCleareance + 0.1:
            aspirationHigh = bottomCleareance + 0.1
        aspiration_count += 1
        # first time we aspirate an extra 50 ul which will be our safety / disposal volume
        protocol.comment("DEBUG: aspirating at {}".format(aspirationHigh)+" high and at {}".format(aspirationRate)+" rate")
        pipette_multi.aspirate(aspirated+safeVolume,stock_reservoir.wells_by_name()[reservoir_column].bottom(aspirationHigh-bottomCleareance),rate=aspirationRate)
        count = 0
        # we keep track of how many times we dispense with each aspiration
        # then we keep aspirating what we dispense
        reservoirFill = reservoirFill - aspirated * 8
        aspirationHigh = reservoirFill / reservoirTotalVolume * depth 
        for well in range(1,13):
            if count >= aspirated/dispensevolume:
                aspirationRate = 0.2 + reservoirFill / reservoirInitialFill * 0.8
                if aspirationHigh < bottomCleareance + 0.1:
                    aspirationHigh = bottomCleareance + 0.1
                protocol.comment("DEBUG: aspirating at {}".format(aspirationHigh)+" high and at {}".format(aspirationRate)+" rate")
                pipette_multi.aspirate(aspirationvolume,stock_reservoir.wells_by_name()[reservoir_column].bottom(aspirationHigh-bottomCleareance),rate=aspirationRate)
                aspirated = aspirationvolume
                reservoirFill = reservoirFill - aspirated * 8
                aspirationHigh = reservoirFill / reservoirTotalVolume * depth 
                aspiration_count += 1
                count = 0
            pipette_multi.dispense(dispensevolume,plate.wells_by_name()['A{}'.format(well)])
            count += 1
        
        pipette_multi.blow_out(stock_reservoir.wells_by_name()[reservoir_column]) #This should't be done after every single plate but after the end of all of theme. This is a fix for P300 pipette tips problem.
    # dispose the tips
    pipette_multi.drop_tip()
