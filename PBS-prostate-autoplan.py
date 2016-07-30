# Script by:
#   Grayden MacLennan and Alex Goughenour
#   grayden.maclennan@seattleprotons.org, alex.goughenour@seattleprotons.org
#   Seattle Proton Therapy Center

#   RayStation version: 4.7.2.5
#   Selected patient: ...

from connect import *
from datetime import datetime




############################################################
# IMPORT ENVIRONMENT VARIABLES
#


patient = get_current("Patient")

examination = get_current("Examination")

db = get_current("PatientDB")



############################################################
# Pre-run error checking
#

# verify that CTV exists
# verify that PTVEval exists
#  - can this be template-specific?
# verify that no plan named "Prostate7920" already exists
# verify that no plan named "DRRs" already exists
# verify that isocenter POI does not already exist


# extract DateTime object that doesn't play nice
seriesdateraw = examination.GetExaminationDateTime()

# convert it to a string
seriesdatestring = "{}".format(seriesdateraw)

# parse the string back into a normal datetime object
seriesdateproperdatetime = datetime.strptime(seriesdatestring, "%m/%d/%Y %H:%M:%S")

# use the datetime string formatting tool to rearrange the parts
reformatteddatestring = datetime.strftime(seriesdateproperdatetime,"%m%d%Y")

# create a name with "RTPCT" on the front
concatenatedname = "RTPCT{}".format(reformatteddatestring)

# rename the examination
examination.Name = concatenatedname

#set the CT-ED table
examination.EquipmentInfo.SetImagingSystemReference(ImagingSystemName="120kVpSEAPBS13")


############################################################
# CREATE THE "Prostate7920" PLAN
#

Prostate7920Plan = patient.AddNewPlan(
					PlanName="Prostate7920",
					PlannedBy="",
					Comment="",
					ExaminationName=examination.Name,
					AllowDuplicateNames=False)

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



#---------------------------------------------------------
# Create DRR version of the plan
#---------------------------------------------------------


DRRPlan = patient.AddNewPlan(
					PlanName="DRRs",
					PlannedBy="",
					Comment="",
					ExaminationName=examination.Name,
					AllowDuplicateNames=False)


# Set the dose grid size
DRRPlan.SetDefaultDoseGrid(VoxelSize={ 'x': 0.5, 'y': 0.5, 'z': 0.5 })


DRRBeamSet = DRRPlan.AddNewBeamSet(
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

DRRBeamSet.AddDosePrescriptionToRoi(
					RoiName="CTV",
					DoseVolume=100,
					PrescriptionType="DoseAtVolume",
					DoseValue=7920,
					RelativePrescriptionLevel=1,
					AutoScaleDose=False)

# Create Beam 80 (RL SETUP)
DRRbeam80 = DRRBeamSet.CreatePbsIonBeam(
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

DRRbeam80.Number = 80

# Create Beam 81 (PA SETUP R)
DRRbeam81 = DRRBeamSet.CreatePbsIonBeam(
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
DRRbeam82 = DRRBeamSet.CreatePbsIonBeam(
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
DRRbeam83 = DRRBeamSet.CreatePbsIonBeam(
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






############################################################
# Load Clinical Goals Template: Standard Prostate Low_Risk
#

Prostate7920Plan.TreatmentCourse.EvaluationSetup.ApplyClinicalGoalTemplate(
					Template=db.TemplateTreatmentOptimizations['Standard Prostate Low_Risk  '])




					
############################################################
# Load Objectives/Constaints Template: Standard Prostate Low_Risk
#	Loads for both Prostate7920 and DRRPlan
					
Prostate7920Plan.PlanOptimizations[0].ApplyOptimizationTemplate(
					Template=db.TemplateTreatmentOptimizations['Prostate7920_PBS Auto Plan'])

DRRPlan.PlanOptimizations[0].ApplyOptimizationTemplate(
					Template=db.TemplateTreatmentOptimizations['Prostate7920_PBS Auto Plan'])					
					
					
										
# Plan Optimization > Settings > Optimization Settings > Optimization Tolerance
Prostate7920Plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 1E-12

# Plan Optimization > Settings > Optimization Settings > Max number of iterations
Prostate7920Plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 100

#Iterations before spot filtering
Prostate7920Plan.PlanOptimizations[0].OptimizationParameters.PencilBeamScanningProperties.NumberOfIterationsBeforeSpotWeightBounding = 0

#Spot limit margin %
Prostate7920Plan.PlanOptimizations[0].OptimizationParameters.PencilBeamScanningProperties.SpotWeightLimitsMargin = 0.10

#Beam Specific Target Margin (cm)

Prostate7920Plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].LateralTargetMargin = 1

Prostate7920Plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[1].LateralTargetMargin = 1

#Optimize Prostate7920 and normalize CTV to 100%RX on completion

Prostate7920Plan.PlanOptimizations[0].RunOptimization()

Prostate7920BeamSet.NormalizeToPrescription(
					RoiName="CTV",
					DoseValue=7920,
					DoseVolume=100,
					PrescriptionType="DoseAtVolume",
					LockedBeamNames=None,
					EvaluateAfterScaling=True)

# max iterations on DRR = 1

DRRPlan.PlanOptimizations[0].OptimizationParameters.PencilBeamScanningProperties.NumberOfIterationsBeforeSpotWeightBounding = 0

DRRPlan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 1

#run optimization for DRRs

DRRPlan.PlanOptimizations[0].RunOptimization()



############################################################
# Run Standard Prostate Robustness Analysis
#	+/- 3% density eval

Prostate7920BeamSet.ComputePerturbedDose(
					DensityPerturbation=0.03,
					IsocenterShift={ 'x': 0, 'y': 0, 'z': 0 },
					IsDoseConsideredClinical=False,
					OnlyOneDosePerImageSet=False,
					AllowGridExpansion=False,
					ExaminationNames = [examination.Name],
					FractionNumbers=[0],
					ComputeBeamDoses=True)
					
Prostate7920BeamSet.ComputePerturbedDose(
					DensityPerturbation=-0.03,
					IsocenterShift={ 'x': 0, 'y': 0, 'z': 0 },
					IsDoseConsideredClinical=False,
					OnlyOneDosePerImageSet=False,
					AllowGridExpansion=False,
					ExaminationNames = [examination.Name],
					FractionNumbers=[0],
					ComputeBeamDoses=True)

