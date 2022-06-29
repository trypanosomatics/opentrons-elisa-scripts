# opentrons-elisa
Code to run ELISA plate preps and assays using an Opentrons OT-2 Robot

This code contains 3 independent scripts that in concert implement a complete medium-throughput ELISA pipeline, from plate prep (antigen binding), to assay. For clarity the complete protocol (USAGE) is outlined here, highlighting steps that need to be performed at the bench (not on the robot). 

## LABWARE 
With one exception, all labware used by these scripts is [validated by Opentrons](https://labware.opentrons.com). The exception is the Greiner Bio-One 96 Well Half-Area Plate labware that we use for our assays to minimize assay volumes and save on precious samples and reagents. Hence we provide in the repo the JSON containing the custom labware definition for these plates (validated by us at the Trypanosomatics Lab).

## KEY ASSAY INFORMATION
At this first commit, there are many hardcoded logic in the scripts (see code and comments in each script). Currently all assays are run in a final volume of 25 uL. Hence, all antigen binding, primary and secondary Ab incubations are performed using this volume. This is hard-coded in all scripts because the pipetting procedure (multiple dispensing) has been carefully designed with this volume in mind. Also, the logic of how to place source solutions (antigens, serum samples, secondary antibody) in decks, and racks and how to map these to well positions in plates is also hardcoded in the scripts. In general I've tried to made the scripts simple enough so that they can be adapted with little or no change to other assay strategies (see ALTERNATIVE USES below).   

## ELISA PIPELINE / PROTOCOL 

### DAY 1 
1. Prepare 24 antigens for binding (dilute at working concentration in binding buffer) and place them in the first three columns of a [NEST 96 Deepwell Plate 2mL](https://labware.opentrons.com/nest_96_wellplate_2ml_deep?category=wellPlate)
2. Run elisa-plate-prep-ot2.py script on Opentrons OT-2
3. Incubate at desired temperature in humidified chamber overnight


### DAY 2
1. Prepare each primary antibody (dilute at working concentration in 5% non-fat dry milk (NFDM)), in a 1.5 mL or 2 mL eppendorf tube, and place each tube in an [Opentrons 24 Tube Rack](https://labware.opentrons.com/opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap?category=tubeRack), see comments in next script for how to place tubes in the rack.
2. Run elisa-plate-assay-primary-Ab-ot2.py on Opentrons OT-2
3. Incubate for 1h at room temperature
4. Wash Plates (at the bench) 5 times
5. Prepare 20 mL secondary antibody (dilute at working concentration in 5% non-fat dry milk (NFDM), and distribute this volume in the first two columns/reservoirs of a [NEST 12 Well Reservoir 15 mL](https://labware.opentrons.com/nest_12_reservoir_15ml?category=reservoir)
6. Run elisa-plate-assay-secondary-Ab-ot2 on Opentrons OT-2
7. Incubate for 1h at room temperature
8. Wash Plates (at the bench) 5 times
9. Read Plates

This outline contains only a brief overview of the protocol, it is not exhaustively detailed ... see comments within scripts for more information.

## ALTERNATIVE USES OF THIS PROTOCOL
This protocol can be easily adapted with little or no change to the scripts to the following situations: 

 * assay each antigen in quadruplicate instead of duplicate
   * in this case just reduce in half the number of antigens and place each antigen twice in the source NEST deep well plate, taking care to keep the two duplicates of each antigen in the same column (e.g. 4 antigens per column = total 12 antigens)
   * alternatively to obtain the same result, keep the same antigens but instead reduce in half the number of primary antibodies, taking care to read and understand the sera map in the corresponding script to place correctly the experimental samples in the 24 Tube Rack.
 * run half the plates with one secondary antibody, and the other half with another 
   * in this case just **place 2ndary Ab ONE in column/reservoir 1** of NEST 12 reservoir, and **2ndary Ab TWO in column/reservoir 2**
   * with these changes, plates 1-4 will be assayed with 2dnary Ab ONE, and plates 5-8 with 2ndary Ab TWO
