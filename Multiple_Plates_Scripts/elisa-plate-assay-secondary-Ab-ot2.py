from opentrons import protocol_api
import math
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



def run(protocol: protocol_api.ProtocolContext):

    # SET Configuration TO RUN:----------------------------------------------------------------------------------------------------------------------------------------------------
    number_plates = 1
    pipette = 300
    pipette_position = "left"
    dispensevolume=100
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    

    # LOAD tips and pipette
    tiprack_11 = protocol.load_labware('opentrons_96_tiprack_300ul', '10')
    if (pipette == 50):
        pipette_multi = protocol.load_instrument('p50_multi', pipette_position, tip_racks=[tiprack_11])
    if (pipette == 300):
        pipette_multi = protocol.load_instrument('p300_multi', pipette_position, tip_racks=[tiprack_11])
    
    # LOAD the reservoir containing the secondary antibody
    stock_reservoir = protocol.load_labware('nest_12_reservoir_15ml', '11')

    # LOAD our ELISA plates (8) in two sets of 4 plates each 
    elisa_plates=[]
    for plate in range(1,(number_plates+1),1):
        elisa_plates.append(protocol.load_labware('greinerbioone_96_wellplate_175ul', plate, label="ELISA Plate {}".format(plate)))

    # we will now iterate plates
    # in this way, this script can be reused -- if one wishes, and without changes --
    # to assay half the plates with one secondary antibody an the other half with another
    # just by dispensing different secondary Abs in slots 1 & 2 of the reservoir
    
    reservoirTotalVolume = 15000 #volume in ul taken from manual
    deadVolume = 400
    
    if (pipette == 50):
        aspirationvolume=25
    if (pipette == 300):
        aspirationvolume=200
    
    if (pipette >= 50 + dispensevolume):
        safeVolume = 50
    else:
        if (pipette >= 25 + dispensevolume):
            safeVolume = 25
    
    number_reservoirs = math.ceil((safeVolume * 8 + 350 + deadVolume + 96 * dispensevolume * number_plates) / reservoirTotalVolume)
    
    reservoirInitialFill = (96 * dispensevolume * number_plates) / number_reservoirs + deadVolume + 50 * 8
    protocol.comment("{}".format(number_reservoirs)+" NEST 12 reservoir containing:")
    protocol.comment("{}".format(reservoirInitialFill + 350)+"ul")
    reservoirFill = reservoirInitialFill 
    depth = 26.86 #depth in mm taken from manual
    aspirationHigh = reservoirFill / reservoirTotalVolume * depth 
    
    # plates 1-4 we use secondary Ab from A1
    secondary_ab_stocks = ['A1','A2','A3','A4','A5','A6','A7','A8','A9','A10','A11','A12']
    ab_stock = 0
    secondary_ab = secondary_ab_stocks[ab_stock]
    pipette_multi.pick_up_tip()
    # we keep track of how many times we dispense with each aspiration
    
    # then we keep aspirating what we dispense
    

    
    bottomCleareance = 3
    


    for plate in elisa_plates:
        count = 0
        aspirated = aspirationvolume
        
        aspirationRate = 0.2 + reservoirFill / reservoirTotalVolume * 0.8
        if aspirationHigh < bottomCleareance + 0.1:
            aspirationHigh = bottomCleareance + 0.1
        protocol.comment("Controling Fill {}".format(reservoirFill)+"ul left")
        if reservoirFill < deadVolume+aspirationvolume*8:
            old_secondary_ab = secondary_ab
            ab_stock = ab_stock + 1
            secondary_ab = secondary_ab_stocks[ab_stock]
            pipette_multi.blow_out(stock_reservoir.wells_by_name()[secondary_ab])
            pipette_multi.transfer(50 + reservoirFill/8,stock_reservoir.wells_by_name()[old_secondary_ab].bottom(aspirationHigh-bottomCleareance),stock_reservoir.wells_by_name()[secondary_ab].bottom(aspirationHigh-bottomCleareance),new_tip = 'never')
            reservoirFill = reservoirFill + safeVolume * 8 + reservoirInitialFill 
            aspirationHigh = reservoirFill / reservoirTotalVolume * depth
            aspirationRate = 0.2 + reservoirFill / reservoirTotalVolume * 0.8
        pipette_multi.aspirate(aspirated+safeVolume,stock_reservoir.wells_by_name()[secondary_ab].bottom(aspirationHigh-bottomCleareance),rate=aspirationRate)
        reservoirFill = reservoirFill - (aspirated + safeVolume) * 8
        aspirationHigh = reservoirFill / reservoirTotalVolume * depth 
        for well in range(1,13):
            if count == aspirated/dispensevolume:
                aspirationRate = 0.2 + reservoirFill / reservoirTotalVolume * 0.8
                if aspirationHigh < bottomCleareance + 0.1:
                    aspirationHigh = bottomCleareance + 0.1
                protocol.comment("Controling Fill {}".format(reservoirFill)+"ul left")
                if reservoirFill < deadVolume+aspirationvolume*8:
                    old_secondary_ab = secondary_ab
                    ab_stock = ab_stock + 1
                    secondary_ab = secondary_ab_stocks[ab_stock]
                    pipette_multi.blow_out(stock_reservoir.wells_by_name()[secondary_ab])
                    pipette_multi.transfer(50 + reservoirFill/8,stock_reservoir.wells_by_name()[old_secondary_ab].bottom(aspirationHigh-bottomCleareance),stock_reservoir.wells_by_name()[secondary_ab].bottom(aspirationHigh-bottomCleareance),new_tip = 'never')
                    reservoirFill = reservoirFill + safeVolume * 8+ reservoirInitialFill
                    aspirationHigh = reservoirFill / reservoirTotalVolume * depth
                    aspirationRate = 0.2 + reservoirFill / reservoirTotalVolume * 0.8
                pipette_multi.aspirate(aspirationvolume,stock_reservoir.wells_by_name()[secondary_ab].bottom(aspirationHigh-bottomCleareance),rate=aspirationRate)
                aspirated = aspirationvolume
                reservoirFill = reservoirFill - aspirated * 8
                aspirationHigh = reservoirFill / reservoirTotalVolume * depth 
                count = 0
            pipette_multi.dispense(dispensevolume,plate.wells_by_name()['A{}'.format(well)])
            count += 1
        if reservoirFill < deadVolume + aspirationvolume * 8 & elisa_plates.index(plate) < len(elisa_plates):
            old_secondary_ab = secondary_ab
            ab_stock = ab_stock + 1
            secondary_ab = secondary_ab_stocks[ab_stock]
            pipette_multi.blow_out(stock_reservoir.wells_by_name()[secondary_ab])
            pipette_multi.transfer(50 + reservoirFill/8,stock_reservoir.wells_by_name()[old_secondary_ab].bottom(aspirationHigh-bottomCleareance),stock_reservoir.wells_by_name()[secondary_ab].bottom(aspirationHigh-bottomCleareance),new_tip = 'never')
            reservoirFill = reservoirFill + safeVolume * 8 + reservoirInitialFill
            aspirationHigh = reservoirFill / reservoirTotalVolume * depth
            aspirationRate = 0.2 + reservoirFill / reservoirTotalVolume * 0.8
            pipette_multi.blow_out(stock_reservoir.wells_by_name()[secondary_ab])
        else:
            pipette_multi.blow_out(stock_reservoir.wells_by_name()[secondary_ab])
    # dispose the tips
    pipette_multi.drop_tip()




