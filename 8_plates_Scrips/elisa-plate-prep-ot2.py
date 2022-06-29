from opentrons import protocol_api

#import json
#with open('C:/Users/ferna/AppData/Roaming/Opentrons/labware/Greiner Bio-One 96 Well Plate Half-Area 175 uL.json') as labware_file:
#    greinerbioone_96_wellplate_175ul = json.load(labware_file)

metadata = {
    'apiLevel' : '2.4',
    'protocolName': 'ELISA PLATE PREP -- 3 COLUMNS x 4 REPLICATES x 8 PLATES',
    'author': 'Fernan Aguero <fernan@iib.unsam.edu.ar>',
    'source': 'Trypanosomatics Lab -- Custom Protocol'
}

# EXPLANATION 
# the idea here is to produce 4 replicates of each antigen in the source plate, while also
# filling the destination plate. Antigens are placed in wells in columns 1, 2 & 3 of source plate,
# and will end up in the destination plate as per the following map:
# Source Plate: columns 1 2 3 
#                       | | |
#                       | | ------------------------------
#                       | |                     |  |  |  |
#                       | --------------------  |  |  |  |
#                       |           |  |  |  |  |  |  |  |
#                       |---------  |  |  |  |  |  |  |  |
#                       |  |  |  |  |  |  |  |  |  |  |  |
# Destination Plate:   01 02 03 04 05 06 07 08 09 10 11 12 

# REQUIRES
# TIPRACK 300 ul with 3 complete columns with tips in SLOT 11
# MULTI p300 PIPETTE mounted on the LEFT side OF OT-2 arm 
# ELISA PLATES (Greiner Bio-One 96well Half-Area) in SLOTS 1-8
# NEST 96 deep well 2mL plate in SLOT 10 
#   with wells in columns 1-3 containing 1mL antigen at the working dilution (24 antigens)
# the protocol will replicate each antigen 4 times in each plate as per the map above

# JUST BEFORE RUNNING THE PROTOCOL
# Prepare dilution of antigens in binding buffer at the desired concentration
# and place 1mL of each antigen in wells A1 through H3 (3 columns, 24 wells)

#This protocol takes about 5 minutes
# START our opentrons protocol
def run(protocol: protocol_api.ProtocolContext):
    # LOAD tips and pipette
    tiprack_11 = protocol.load_labware('opentrons_96_tiprack_300ul', '10')
    pipette_multi = protocol.load_instrument('p300_multi', 'left', tip_racks=[tiprack_11])
    # LOAD the stock plate containing antigens
    stock_plate = protocol.load_labware('nest_96_wellplate_2ml_deep', '11')
    # maybe also try usascientific_96_wellplate_2.4ml_deep
    depth = 42
    reservoirTotalVolume = 2000
    reservoirFill = 1000
    aspirationHigh = reservoirFill / reservoirTotalVolume * depth
    bottomCleareance = 8
    # LOAD our ELISA plates (8)
    elisa_plates=[]
    for plate in range(1,9,1):
        elisa_plates.append(protocol.load_labware('greinerbioone_96_wellplate_175ul', plate, label="ELISA Plate {}".format(plate)))


    # DEFINE our three blocks of destination columns as per our map above
    dest_columns = [ ["1", "2", "3", "4"], ['5', '6', '7', '8'], ['9', '10', '11', '12'] ]
    # we will now iterate blockwise so as to use a single tip for all replicates
    # of the same antigen
    block_count=1
    aspirated = 0
    for destination in dest_columns:
        aspirated = 200
        aspirationRate = 0.2 + reservoirFill / 1000 * 0.8
        if aspirationHigh < bottomCleareance + 0.1:
            aspirationHigh = bottomCleareance + 0.1
        protocol.comment("DEBUG: aspirating at {}".format(aspirationHigh)+" high and at {}".format(aspirationRate)+" rate")
        source_column = stock_plate.wells_by_name()['A{}'.format(block_count)]
        pipette_multi.pick_up_tip()
        # first time we aspirate an extra 50 ul which will be our safety / disposal volume
        pipette_multi.aspirate(250, source_column.bottom(aspirationHigh-bottomCleareance),rate=aspirationRate)
        # then we keep aspirating what we dispense
        aspirationvolume=200
        dispensevolume=25
        reservoirFill = reservoirFill - aspirated
        aspirationHigh = reservoirFill / reservoirTotalVolume * depth 
        count=0
        for plate in elisa_plates:
            for col in destination:
                if count == 8:
                    aspirated = 200
                    aspirationRate = 0.2 + reservoirFill / 1000 * 0.8
                    if aspirationHigh < bottomCleareance + 0.1:
                        aspirationHigh = bottomCleareance + 0.1
                    protocol.comment("DEBUG: aspirating at {}".format(aspirationHigh)+" high and at {}".format(aspirationRate)+" rate")
                    pipette_multi.aspirate(aspirationvolume, source_column.bottom(aspirationHigh-bottomCleareance),rate=aspirationRate)
                    aspirated = aspirationvolume
                    reservoirFill = reservoirFill - aspirated
                    aspirationHigh = reservoirFill / reservoirTotalVolume * depth 
                    count = 0
                pipette_multi.dispense(dispensevolume, plate.wells_by_name()['A{}'.format(col)], rate=1.0)
                count += 1
        # when we finish this block we blow out the safety volume back to the source
        pipette_multi.blow_out(source_column)
        # dispose the tips
        pipette_multi.drop_tip()
        # and start a new block
        block_count += 1
        reservoirFill = 1000
        aspirationHigh = reservoirFill / reservoirTotalVolume * depth 
