# Environment of a Meshroom install from source (docs/INSTALL.md, "From source"): edit the paths, then
#   source scripts/env_source.sh
AV=/path/to/AliceVision            # nightly build or install folder
MR=/path/to/Meshroom               # clone of Meshroom develop with the fixes merged
VENV=/path/to/meshroom-venv
export ALICEVISION_ROOT=$AV
export LD_LIBRARY_PATH=$AV/lib64:$AV/lib     # no /usr/local/cuda/lib64: it hides the CUDA libraries of the plugins
export PATH=$VENV/bin:$AV/bin:/usr/local/bin:/usr/bin:/bin
export PYTHONPATH=$MR:$AV/lib64/python
export ALICEVISION_SENSOR_DB=$AV/share/aliceVision/cameraSensors.db
export ALICEVISION_VOCTREE=$AV/share/aliceVision/vlfeat_K80L3.SIFT.tree
export ALICEVISION_SPHERE_DETECTION_MODEL=$AV/share/aliceVision/sphereDetection_Mask-RCNN.onnx
export ALICEVISION_COLORCHARTDETECTION_MODEL_FOLDER=$AV/share/aliceVision/ColorChartDetectionModel
export MESHROOM_NODES_PATH=$AV/share/meshroom
export MESHROOM_PIPELINE_TEMPLATES_PATH=$AV/share/meshroom
# plugins; do not create this folder beforehand (Meshroom copies the official registry only into a new folder)
export MESHROOM_LOCAL_PLUGINS_PATH=/path/to/meshroom-plugins
export RDS_SAM3_MODEL_PATH=/path/to/sam3.pt
