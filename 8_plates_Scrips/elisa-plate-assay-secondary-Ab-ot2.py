from opentrons import protocol_api

#import json
#with open('C:/Users/ferna/AppData/Roaming/Opentrons/labware/Greiner Bio-One 96 Well Plate Half-Area 175 uL.json') as labware_file:
#    greinerbioone_96_wellplate_175ul = json.load(labware_file)

metadata = {
    'apiLevel' : '2.4',
    'protocolName': 'ELISA ASSAY PREP -- SECONDARY ANTIBODY',
    'author': 'Fernan Aguero <fernan@iib.unsam.edu.ar>',
    'source': 'Trypanosomatics Lab -- Custom Protocol'
}

# EXPLANATION 
# The idea of this protocol is to dispense secondary antibody in all plates.
# This script is very simple and will dispense secondary antibody in all wells for all 8 plates
# but because we exceed the volume of one reservoir column, here we're using two reservoir columns
# Secondary Antibody in Reservoir: 
#  columns 1 2  
#          | | 
#          | | --> PLATES 5-8
#          | 
#          | ----> PLATES 1-4


# REQUIRES
# TIPRACK 300 ul with column 1 complete with tips in SLOT 11
# MULTI p300 PIPETTE mounted on the LEFT side OF OT-2 arm 
# ELISA PLATES (Greiner Bio-One 96well Half-Area) in SLOTS 1-8
# NEST 12 reservoir (15 mL each) in SLOT 10 
# filled with secondary antibody at the working dilution in columns 1 + 2 (10.35 mL + 10 mL) 
# the protocol uses 9.6 mL for plates 1-4 from column 1 of the reservoir
# and 9.6 mL for plates 5-8 from column 2 of the reservoir
# so we need an extra volume in each reservoir to account for bed volume for pipetting

# JUST BEFORE RUNNING THE PROTOCOL
# Prepare dilution of secondary antibody in TBS + 5% non-fat dry milk (NFDM)
# e.g. for a 1:1000 dilution, mix 20 ul Secondary Antibody in 19.98 mL NFDM

# START our opentrons protocol
# This protocol takes 4 minutes (last update 17/2/2021) G1 pipette
# This protocol takes 5 minutes (last update 4/8/2021) G2 pipette

def run(protocol: protocol_api.ProtocolContext):
    # LOAD tips and pipette
    tiprack_11 = protocol.load_labware('opentrons_96_tiprack_300ul', '10')
    pipette_multi = protocol.load_instrument('p300_multi', 'left', tip_racks=[tiprack_11])
    # LOAD the reservoir containing the secondary antibody
    stock_reservoir = protocol.load_labware('nest_12_reservoir_15ml', '11')

    # LOAD our ELISA plates (8) in two sets of 4 plates each 
    elisa_plates=[]
    for plate in range(1,9,1):
        elisa_plates.append(protocol.load_labware('greinerbioone_96_wellplate_175ul', plate, label="ELISA Plate {}".format(plate)))

    # we will now iterate plates
    # in this way, this script can be reused -- if one wishes, and without changes --
    # to assay half the plates with one secondary antibody an the other half with another
    # just by dispensing different secondary Abs in slots 1 & 2 of the reservoir
    
    reservoirTotalVolume = 15000 #volume in ul taken from manual
    reservoirFill = 10000
    depth = 26.86 #depth in mm taken from manual
    aspirationHigh = reservoirFill / reservoirTotalVolume * depth 
    
    # plates 1-4 we use secondary Ab from A1
    secondary_ab = 'A1'
    pipette_multi.pick_up_tip()
    # we keep track of how many times we dispense with each aspiration
    
    # then we keep aspirating what we dispense
    aspirationvolume=100
    dispensevolume=25
    aspiration_count = 0
    aspirated = 0
    bottomCleareance = 3
    for plate in elisa_plates:
        count = 0
        aspirated = 200
        aspirationRate = 0.2 + reservoirFill / 10000 * 0.8
        if aspirationHigh < bottomCleareance + 0.1:
            aspirationHigh = bottomCleareance + 0.1
        aspiration_count += 1
        pipette_multi.aspirate(250,stock_reservoir.wells_by_name()[secondary_ab].bottom(aspirationHigh-bottomCleareance),rate=aspirationRate)
        reservoirFill = reservoirFill - aspirated * 8
        aspirationHigh = reservoirFill / reservoirTotalVolume * depth 
        for well in range(1,13):
            if count == aspirated/dispensevolume:
                aspirationRate = 0.2 + reservoirFill / 10000 * 0.8
                if aspirationHigh < bottomCleareance + 0.1:
                    aspirationHigh = bottomCleareance + 0.1
                pipette_multi.aspirate(aspirationvolume,stock_reservoir.wells_by_name()[secondary_ab].bottom(aspirationHigh-bottomCleareance),rate=aspirationRate)
                aspirated = aspirationvolume
                reservoirFill = reservoirFill - aspirated * 8
                aspirationHigh = reservoirFill / reservoirTotalVolume * depth 
                aspiration_count += 1
                count = 0
            pipette_multi.dispense(dispensevolume,plate.wells_by_name()['A{}'.format(well)])
            count += 1
        if aspiration_count == 8:
            secondary_ab = 'A2'
            reservoirFill = 10400
            aspirationHigh = reservoirFill / reservoirTotalVolume * depth
            aspirationRate = 0.2 + reservoirFill / 10000 * 0.8
        pipette_multi.blow_out(stock_reservoir.wells_by_name()[secondary_ab])
    # dispose the tips
    pipette_multi.drop_tip()
