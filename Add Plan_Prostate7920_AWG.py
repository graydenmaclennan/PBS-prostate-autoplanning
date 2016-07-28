# Script by:
#   Grayden MacLennan and Alex Goughenour
#   grayden.maclennan@seattleprotons.org, alex.goughenour@seattleprotons.org
#   Seattle Proton Therapy Center

#   RayStation version: 4.7.2.5
#   Selected patient: ...

from connect import *

############################################################
#
#


############################################################
# Pre-run error checking
#

# verify that CTV exists
# verify that no plan named "Prostate7920" already exists
# verify that no plan named "DRRs" already exists
# verify that isocenter POI does not already exist




############################################################
# IMPORT ENVIRONMENT VARIABLES
#
print "going to try to import environment variables"

try:
  print "trying to get Patient"
  patient = get_current("Patient")
except:
  print "had a problem loading the patient"

try:
  print "trying to get BeamSet"
  beam_set = get_current("BeamSet")
except:
  print "had a problem loading the BeamSet"

try:
  print "trying to get Examination"
  examination = get_current("Examination")
except:
  print "had a problem loading the Examination"

try:
  print "trying to get PatientDB"
  db = get_current("PatientDB")
except:
  print "had a problem loading the PatientDB"

print "got the environment variables"


############################################################
# CREATE THE "Prostate7920" PLAN
#
print "going to try adding a new plan"
print examination.Name
Prostate7920Plan = patient.AddNewPlan(
					PlanName="Prostate7920",
					PlannedBy="",
					Comment="",
					ExaminationName=examination.Name,
					AllowDuplicateNames=False)
print "made it past the attempt to add a new plan"

# Set the dose grid size
Prostate7920Plan.SetDefaultDoseGrid(VoxelSize={ 'x': 0.3, 'y': 0.3, 'z': 0.3 })


############################################################
# EXTRACT AND SET ISOCENTER
#
structure_set = Prostate7920Plan.GetStructureSet()

CTVcentroid = structure_set.RoiGeometries["CTV"].GetCenterOfRoi()

settableIsocenter = { 'x': CTVcentroid.x, 'y': CTVcentroid.y, 'z': CTVcentroid.z,}

CreateIsocenterPOI = patient.PatientModel.CreatePoi(
					Examination=examination,
					Point= settableIsocenter,
					Volume=0,
					Name="Isocenter",
					Color="Lime",
					Type="Isocenter")



############################################################
# CREATE A NEW BEAMSET
#
Prostate7920BeamSet = Prostate7920Plan.AddNewBeamSet(
					Name="Prostate7920",
					ExaminationName=examination.Name,
					MachineName="FBTR1",
					NominalEnergy=0,
					Modality="Protons",
					TreatmentTechnique="ProtonPencilBeamScanning",
					PatientPosition="FeetFirstSupine",
					NumberOfFractions=44,
					CreateSetupBeams=False,
					UseLocalizationPointAsSetupIsocenter=False,
					Comment="")

# Add a prescription to the BeamSet
Prostate7920BeamSet.AddDosePrescriptionToRoi(
					RoiName="CTV",
					DoseVolume=100,
					PrescriptionType="DoseAtVolume",
					DoseValue=7920,
					RelativePrescriptionLevel=1,
					AutoScaleDose=False)



############################################################
# CREATE BEAMS
#
MyNewBeam1 = Prostate7920BeamSet.CreatePbsIonBeam(
					SnoutId="25",
					SpotTuneId="4.0",
					RangeShifter="25RS-00",
					MinimumAirGap=None,
					Isocenter=settableIsocenter,
					Name="1",
					Description="G90T0RL",
					GantryAngle=90,
					CouchAngle=0,
					CollimatorAngle=0,
					ApertureBlock=None)

MyNewBeam2 = Prostate7920BeamSet.CreatePbsIonBeam(
					SnoutId="25",
					SpotTuneId="4.0",
					RangeShifter="25RS-00",
					MinimumAirGap=None,
					Isocenter=settableIsocenter,
					Name="2",
					Description="G90T180LL",
					GantryAngle=90,
					CouchAngle=180,
					CollimatorAngle=0,
					ApertureBlock=None)



#-----------------------------------
# Create DRR version of the plan
#-----------------------------------


MyDRRPlan = patient.AddNewPlan(
					PlanName="DRRs",
					PlannedBy="",
					Comment="",
					ExaminationName=examination.Name,
					AllowDuplicateNames=False)

print "made it past the attempt to add a new plan"

# Set the dose grid size
MyDRRPlan.SetDefaultDoseGrid(VoxelSize={ 'x': 0.3, 'y': 0.3, 'z': 0.3 })


MyDRRBeamSet = MyDRRPlan.AddNewBeamSet(
					Name="Prostate7920",
					ExaminationName=examination.Name,
					MachineName="FBTR1_test",
					NominalEnergy=0,
					Modality="Protons",
					TreatmentTechnique="ProtonPencilBeamScanning",
					PatientPosition="FeetFirstSupine",
					NumberOfFractions=44,
					CreateSetupBeams=False,
					UseLocalizationPointAsSetupIsocenter=False,
					Comment="")

MyDRRBeamSet.AddDosePrescriptionToRoi(
					RoiName="CTV",
					DoseVolume=100,
					PrescriptionType="DoseAtVolume",
					DoseValue=7920,
					RelativePrescriptionLevel=1,
					AutoScaleDose=False)

# Create Beam 80 (RL SETUP)
DRRbeam80 = MyDRRBeamSet.CreatePbsIonBeam(
					SnoutId="25",
					SpotTuneId="4.0",
					RangeShifter="25RS-00",
					MinimumAirGap=None,
					Isocenter=settableIsocenter,
					Name="80",
					Description="RL SETUP",
					GantryAngle=90,
					CouchAngle=0,
					CollimatorAngle=0,
					ApertureBlock=None)

# reset beam number to beam 80
# RayStation will count upwards from 80, so no need to renumber subsequent beams
print "going to try to set the beam number"
try:
	DRRbeam80.Number = 80
	print "no errors after setting the beam number of beam 80"
except:
	print "could not set the beam number of beam 80"

# Create Beam 81 (PA SETUP R)
DRRbeam81 = MyDRRBeamSet.CreatePbsIonBeam(
					SnoutId="25",
					SpotTuneId="4.0",
					RangeShifter="25RS-00",
					MinimumAirGap=None,
					Isocenter=settableIsocenter,
					Name="81",
					Description="PA SETUP R",
					GantryAngle=180,
					CouchAngle=0,
					CollimatorAngle=0,
					ApertureBlock=None)

# Create Beam 82 (LL SETUP)
DRRbeam82 = MyDRRBeamSet.CreatePbsIonBeam(
					SnoutId="25",
					SpotTuneId="4.0",
					RangeShifter="25RS-00",
					MinimumAirGap=None,
					Isocenter=settableIsocenter,
					Name="82",
					Description="LL SETUP",
					GantryAngle=90,
					CouchAngle=180,
					CollimatorAngle=0,
					ApertureBlock=None)

# Create Beam 83 (PA SETUP L)
DRRbeam83 = MyDRRBeamSet.CreatePbsIonBeam(
					SnoutId="25",
					SpotTuneId="4.0",
					RangeShifter="25RS-00",
					MinimumAirGap=None,
					Isocenter=settableIsocenter,
					Name="83",
					Description="PA SETUP L",
					GantryAngle=180,
					CouchAngle=180,
					CollimatorAngle=0,
					ApertureBlock=None)

# can this be done by using the template?

#figure out how to optimize





############################################################
# Load Clinical Goals: Standard Prostate Low_Risk
#

Prostate7920Plan.TreatmentCourse.EvaluationSetup.ApplyClinicalGoalTemplate(
					Template=db.TemplateTreatmentOptimizations['Standard Prostate Low_Risk  '])




					
############################################################
# Load Clinical Goals: Standard Prostate Low_Risk
#
					
Prostate7920Plan.PlanOptimizations[0].ApplyOptimizationTemplate(
					Template=db.TemplateTreatmentOptimizations['Prsotate7920_AWG'])

					
					
					
					
					
					
					
					
					
					
############################################################
# Attempting to: Edit Beam Specific Target Margin
#

# Unscriptable Action 'Edit beam optimization settings (1, Beam Set: Prostate7920)' Completed : EditIonBeamOptimizationSettingsAction(...)

# Unscriptable Action 'Edit beam optimization settings (2, Beam Set: Prostate7920)' Completed : EditIonBeamOptimizationSettingsAction(...)









