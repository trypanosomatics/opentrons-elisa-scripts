from opentrons import protocol_api
import numpy as np

# import json
# with open('C:/Users/ferna/AppData/Roaming/Opentrons/labware/Greiner Bio-One 96 Well Plate Half-Area 175 uL.json') as labware_file:
#    greinerbioone_96_wellplate_175ul = json.load(labware_file)

metadata = {
    'apiLevel' : '2.9',
    'protocolName': 'ELISA PLATE PEPTIDE DILUTIONS PREPARATION',
    'author': 'Leo Bracco',
    'source': 'Trypanosomatics Lab -- Custom Protocol'
}


#dil: 1:250
#vol final: 600
#10 ul peptido + 590 ul PBS
def run(protocol: protocol_api.ProtocolContext):

    # SET TO RUN:----------------------------------------------------------------------------------------------------------------------------------------------------
    vol_final = 1700
    dilution_peptide = 100 #factor de la dilución de los péptidos
    dilution_BSA = 825
    dilution_M7 = 825 #cada pept termina en una dilución de 1 en 825
    dilution_NAG = 100 
    dilution_Ag2 = 160


    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    # LOAD tips and pipette
    tiprack_grande = protocol.load_labware('opentrons_96_tiprack_1000ul', '10')
    tiprack_chico = protocol.load_labware('opentrons_96_tiprack_20ul', '7')
    pipette_single_1000 = protocol.load_instrument('p1000_single','left' , tip_racks=[tiprack_grande])
    pipette_single_20 = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tiprack_chico])
    peptide_plate = protocol.load_labware('nest_96_wellplate_2ml_deep', '4')
    peptide_stock_plate_impares = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '1')
    peptide_stock_plate_pares = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '2')
    pbs_stock = protocol.load_labware('opentrons_6_tuberack_falcon_50ml_conical','3')
    
    
    peptide_control_map = {
        '40940':   {'origin_stock':'1','from' :'A1','to' : {'A1'},'dilution':'peptide'},
        '40941':   {'origin_stock':'1','from' :'A2','to' : {'B1'},'dilution':'peptide'},
        '40942':  {'origin_stock':'1','from' :'A3','to' : {'C1'},'dilution':'peptide'},
        '40943':  {'origin_stock':'1','from' :'A4','to' : {'D1'},'dilution':'peptide'},
        '40944':  {'origin_stock':'1','from' :'A5','to' : {'E1'},'dilution':'peptide'},
        '40945':   {'origin_stock':'1','from' :'A6','to' : {'F1'},'dilution':'peptide'},
        '40946':   {'origin_stock':'1','from' :'B1','to' : {'G1'},'dilution':'peptide'},
        '40947':   {'origin_stock':'1','from' :'B2','to' : {'H1'},'dilution':'peptide'},
        '40948':   {'origin_stock':'1','from' :'B3','to' : {'A2'},'dilution':'peptide'},
        '40950':  {'origin_stock':'1','from' :'B4','to' : {'B2'},'dilution':'peptide'},
        '40951':  {'origin_stock':'1','from' :'B5','to' : {'C2'},'dilution':'peptide'},
        '40952':  {'origin_stock':'1','from' :'B6','to' : {'D2'},'dilution':'peptide'},
        '40953':  {'origin_stock':'1','from' :'C1','to' : {'E2'},'dilution':'peptide'},
        '40954':  {'origin_stock':'1','from' :'C2','to' : {'F2'},'dilution':'peptide'},
        '40955':  {'origin_stock':'1','from' :'C3','to' : {'G2'},'dilution':'peptide'},
        '40956':  {'origin_stock':'1','from' :'C4','to' : {'H2'},'dilution':'peptide'},
        '40959':  {'origin_stock':'1','from' :'C5','to' : {'A3'},'dilution':'peptide'},
        '40960':  {'origin_stock':'1','from' :'C6','to' : {'B3'},'dilution':'peptide'},
        '40961':  {'origin_stock':'1','from' :'D1','to' : {'C3'},'dilution':'peptide'},
        '40963':   {'origin_stock':'2','from' :'A1','to' : {'H12'},'dilution':'peptide'},
        '40965':   {'origin_stock':'2','from' :'A2','to' : {'G12'},'dilution':'peptide'},
        '40966':  {'origin_stock':'2','from' :'A3','to' : {'F12'},'dilution':'peptide'},
        '40968':  {'origin_stock':'2','from' :'A4','to' : {'E12'},'dilution':'peptide'},
        '40969':  {'origin_stock':'2','from' :'A5','to' : {'D12'},'dilution':'peptide'},
        '41047':   {'origin_stock':'2','from' :'A6','to' : {'C12'},'dilution':'peptide'},
        '41048':   {'origin_stock':'2','from' :'B1','to' : {'B12'},'dilution':'peptide'},
        '41049':   {'origin_stock':'2','from' :'B2','to' : {'A12'},'dilution':'peptide'},
        '41050':   {'origin_stock':'2','from' :'B3','to' : {'H11'},'dilution':'peptide'},
        '41051':  {'origin_stock':'2','from' :'B4','to' : {'G11'},'dilution':'peptide'},
        '41052':  {'origin_stock':'2','from' :'B5','to' : {'F11'},'dilution':'peptide'},
        '41053':  {'origin_stock':'2','from' :'B6','to' : {'E11'},'dilution':'peptide'},
        '41055':  {'origin_stock':'2','from' :'C2','to' : {'C11'},'dilution':'peptide'},
        '41056':  {'origin_stock':'2','from' :'C3','to' : {'B11'},'dilution':'peptide'},
        '41057':  {'origin_stock':'2','from' :'C4','to' : {'A11'},'dilution':'peptide'},
        'NAG1-1A':  {'origin_stock':'2','from' :'C5','to' : {'H10'},'dilution':'NAG'},
        'NAG1-2B':  {'origin_stock':'2','from' :'C6','to' : {'G10'},'dilution':'NAG'},
        'NAG1-3C':  {'origin_stock':'2','from' :'D1','to' : {'F10'},'dilution':'NAG'},
        'ps-tag':   {'origin_stock':'1','from' :'D2','to' : {'D3','E10'},'dilution':'peptide'},
        'BSA':   {'origin_stock':'1','from' :'D3','to' : {'E3','D10'},'dilution':'BSA'},
        'PS-Ag2':   {'origin_stock':'1','from' :'D5','to' : {'G3','B10'},'dilution':'Ag2'},
        'Ag2-Ps':   {'origin_stock':'1','from' :'D6','to' : {'H3','A10'},'dilution':'Ag2'},
        'm1':   {'origin_stock':'1','from' :'D4','to' : {'F3','C10'},'dilution':'M7'},
        'm2':   {'origin_stock':'2','from' :'C1','to' : {'F3','C10'},'dilution':'M7'},
        'm3':   {'origin_stock':'2','from' :'D2','to' : {'F3','C10'},'dilution':'M7'},
        'm4':   {'origin_stock':'2','from' :'D3','to' : {'F3','C10'},'dilution':'M7'},
        'm5':   {'origin_stock':'2','from' :'D4','to' : {'F3','C10'},'dilution':'M7'},
        'm6':   {'origin_stock':'2','from' :'D5','to' : {'F3','C10'},'dilution':'M7'},
        'm7':   {'origin_stock':'2','from' :'D6','to' : {'F3','C10'},'dilution':'M7'},
        'PBS':   {'origin_stock':'PBS','from' :'PBS','to' : {'D11'},'dilution':'PBS'}
    }
    

    pbs_stocks = ["A1", "A2", "A3","B1", "B2", "B3"]
    
    reservoirTotalVolume_PBS = 50000
    reservoirFill_PBS = reservoirTotalVolume_PBS
    depth_PBS = 120.30
    pbs_deadVolume = 600
    # peptide_deadVolume = 1
    
    bottom_clearance_Eppendorfs = 1.2
    bottom_cleareance_DeepWell = 8
    bottomCleareance_PBS = 8
    
    pbsStock_initialVolume = reservoirTotalVolume_PBS
    # peptide_initialVolume = vol_final / dilution
    
    
    pipette_single_1000.pick_up_tip()
    
    #primero transferimos el PBS
    for peptide in peptide_control_map:
        if peptide_control_map[peptide]['dilution'] == 'peptide':
            dilution = dilution_peptide
            volume_to_transfer = vol_final - 1/dilution * vol_final
        elif peptide_control_map[peptide]['dilution'] == 'BSA':
            dilution = dilution_BSA
            volume_to_transfer = vol_final - 1/dilution * vol_final 
        elif peptide_control_map[peptide]['dilution'] == 'M7':
            dilution = dilution_M7
            volume_to_transfer = (vol_final - 7/dilution * vol_final)/7 #porque son 7 péptidos
        elif peptide_control_map[peptide]['dilution'] == 'Ag2':
            dilution = dilution_Ag2
            volume_to_transfer = vol_final - 1/dilution * vol_final
        elif peptide_control_map[peptide]['dilution'] == 'NAG':
            dilution = dilution_Ag2
            volume_to_transfer = vol_final - 1/dilution * vol_final
        elif peptide_control_map[peptide]['dilution'] == 'PBS':
            volume_to_transfer = vol_final
        for destiny in peptide_control_map[peptide]['to']:    
            protocol.comment("DEBUG: peptide = {}".format(peptide))
            protocol.comment("DEBUG: pbsRemain = {}".format(reservoirFill_PBS))
            aspirationHigh = reservoirFill_PBS / reservoirTotalVolume_PBS * depth_PBS 
            protocol.comment("DEBUG: pbsHigh = {}".format(aspirationHigh))
            if aspirationHigh < bottomCleareance_PBS + 0.1:
                aspirationHigh = bottomCleareance_PBS + 0.1
            reservoirFill_PBS = reservoirFill_PBS - volume_to_transfer
            pipette_single_1000.transfer(volume_to_transfer, pbs_stock.wells_by_name()[pbs_stocks[0]].bottom(aspirationHigh-bottomCleareance_PBS), peptide_plate.wells_by_name()[destiny].top(),new_tip='never')
            pipette_single_1000.blow_out(peptide_plate.wells_by_name()[destiny].top())
            if reservoirFill_PBS < volume_to_transfer + pbs_deadVolume:
                pbs_stocks.pop(0)
                reservoirFill_PBS = pbsStock_initialVolume

    pipette_single_1000.drop_tip()
    
    #ahora ponemos los péptidos
    for peptide in peptide_control_map:
        if peptide_control_map[peptide]['origin_stock'] == '1':
            peptide_origin = peptide_stock_plate_impares
        if peptide_control_map[peptide]['origin_stock'] == '2':
            peptide_origin = peptide_stock_plate_pares
        if peptide_control_map[peptide]['dilution'] == 'peptide':
            dilution = dilution_peptide
        elif peptide_control_map[peptide]['dilution'] == 'BSA':
            dilution = dilution_BSA
        elif peptide_control_map[peptide]['dilution'] == 'M7':
            dilution = dilution_M7
        elif peptide_control_map[peptide]['dilution'] == 'Ag2':
            dilution = dilution_Ag2
        elif peptide_control_map[peptide]['dilution'] == 'NAG':
            dilution = dilution_NAG
        elif peptide_control_map[peptide]['dilution'] == 'PBS':
            protocol.comment("DEBUG: peptide = {}".format(peptide))
            continue
        pipette_single_20.pick_up_tip()
        for destiny in peptide_control_map[peptide]['to']:    
            protocol.comment("DEBUG: peptide = {}".format(peptide))
            pipette_single_20.transfer((vol_final/dilution),peptide_origin.wells_by_name()[peptide_control_map[peptide]['from']], peptide_plate.wells_by_name()[destiny],new_tip='never',mix_after = (3,20))
        pipette_single_20.drop_tip() 
    
    #Busco los pocillos del deepwell usados
    destinations = []
    for peptide in peptide_control_map:
        # peptide = "PS-Ag2"
        # peptide = "40969"
        temp_destination = peptide_control_map[peptide]['to']
        if isinstance(temp_destination, str):
            destinations.append(temp_destination)
        else:
            destinations.extend(temp_destination)
        
    destinations = list(dict.fromkeys(destinations))
    #ahora mixeamos todo
    for well in destinations:
        protocol.comment("DEBUG: peptide = {}".format(well))
        pipette_single_1000.pick_up_tip()
        pipette_single_1000.mix(3,900, peptide_plate.wells_by_name()[well].bottom(21))
        pipette_single_1000.drop_tip()  
    

