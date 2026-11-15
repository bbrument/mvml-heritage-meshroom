#!/usr/bin/env python
"""Build the VISART Meshroom templates of templates/.

Common head: CameraInit (MV/ + PS/PS_xx/) -> ImageProcessing (EXR) -> ImageSegmentationSam3 -> FeatureExtraction
-> ImageMatching -> FeatureMatching -> StructureFromMotion -> IntrinsicsTransforming -> ExportImages, then the
photometric stereo (LED-getter: dense photogrammetry of MV as proxy, ConvertSfMFormat, LedGetterLights,
LedGetterPS; or UniMSPS; or LINOUniPS) -> RNbNeuS2, and with an albedo
MeshRemoveUnseenFaces -> Texturing. The Gourdan bone has no separate MV set: it uses the PS-only graph of
build_ps_only (one all-LED reference image per PS folder, named *_all_leds).

The published templates were generated with Meshroom develop edc4b6a2, AliceVision 6f9f58ec and the plugins of the
official registry at meshroomHub/pluginRegistry 266f167.

Usage (with Meshroom and the plugins on the Python path, see docs/INSTALL.md):
    python build_templates.py <output_folder> [name ...]
    python build_templates.py --tree <output_folder>    # the published templates, in the tree of templates/

Names: <object> (LINO-UniPS, normals only), <object>_lino (LINO-UniPS, normals and albedo), <object>_ledgetter
(LED-getter), gourdan_bone_unimsps (Uni-MS-PS), with <object> in warrior, biface, calathos, gourdan_bone.
PUBLISHED maps the names to the files of templates/.
"""
import os
import sys

import meshroom.core
from meshroom.core.graph import Graph

OBJECTS = {
    # name: (SAM3 prompt, mask the dspsift features, add unmasked tag16h5 features)
    "warrior": ("sculpture", False, False),
    "calathos": ("terracotta", True, False),
    "biface": ("stone", True, True),
}

PS_ONLY_OBJECTS = {
    # name: SAM3 prompt
    "gourdan_bone": "bone",
}

# Lights fixed to the camera (biface: 12-LED rig; calathos PS_01-PS_07 and gourdan: RTI dome carrying the camera):
# LED-getter calibrates one set of lights on all the poses lit by the same sequence (LedGetterLights 'Light Rig').
# The warrior is lit by a hand-held flash: its lights are calibrated per pose.
LIGHT_RIG_OBJECTS = {"biface", "calathos", "gourdan_bone"}

# generator name -> path of the published template (templates/ of this repository, same tree as the dataset)
PUBLISHED = {
    "warrior_ledgetter": "warrior/warrior_visart-eccv26.mgt",
    "biface_ledgetter": "biface/biface_visart-eccv26.mgt",
    "calathos_ledgetter": "calathos/calathos_visart-eccv26.mgt",
    "gourdan_bone_unimsps": "gourdan_bone/gourdan_bone_visart-eccv26.mgt",
    "warrior_lino": "warrior/templates/warrior_lino_unips.mgt",
    "biface_lino": "biface/templates/biface_lino_unips.mgt",
    "calathos_lino": "calathos/templates/calathos_lino_unips.mgt",
    "gourdan_bone_lino": "gourdan_bone/templates/gourdan_bone_lino_unips.mgt",
    "gourdan_bone_ledgetter": "gourdan_bone/templates/gourdan_bone_led_getter.mgt",
}


def buildStructureFromMotion(prompt, maskFeatures, turntableTags):
    """Shared MVPS front end: SAM3 masks and SfM on all the images (MV and PS).

    Returns:
        (graph, dict of the nodes reused by the photometric stereo back ends)
    """
    g = Graph("")

    cameraInit = g.addNewNode("CameraInit")

    # Develop the RAW images once (SAM3 cannot read NEF files)
    imageProcessing = g.addNewNode("ImageProcessing", input=cameraInit.output, extension="exr")
    images = imageProcessing.outSfMData

    segmentation = g.addNewNode("ImageSegmentationSam3", input=images, prompt=prompt, extensionOut="png")

    featureExtraction = g.addNewNode("FeatureExtraction", input=images, describerTypes=["dspsift"])
    if maskFeatures:
        g.addEdge(segmentation.output, featureExtraction.masksFolder)
    featuresFolders = [featureExtraction.output]
    describerTypes = ["dspsift"]

    if turntableTags:
        # AprilTags of the turntable lie outside the object mask: detect them on the full image
        tagExtraction = g.addNewNode("FeatureExtraction", input=images, describerTypes=["tag16h5"])
        featuresFolders.append(tagExtraction.output)
        describerTypes.append("tag16h5")

    imageMatching = g.addNewNode("ImageMatching", input=images)
    imageMatching.featuresFolders.resetToDefaultValue()
    for folder in featuresFolders:
        imageMatching.featuresFolders.append(folder)

    featureMatching = g.addNewNode("FeatureMatching", input=imageMatching.input, imagePairsList=imageMatching.output,
                                   featuresFolders=imageMatching.featuresFolders, describerTypes=describerTypes)

    sfm = g.addNewNode("StructureFromMotion", input=featureMatching.input, featuresFolders=featureMatching.featuresFolders,
                       describerTypes=describerTypes)
    sfm.matchesFolders.append(featureMatching.output)

    return g, {"cameraInit": cameraInit, "segmentation": segmentation, "sfm": sfm}


def addUndistortedImages(g, inputSfm, segmentation, outputFileType):
    """Pinhole intrinsics and undistorted exports, with the masks, of the views of inputSfm: ExportImages writes the
    views of its target SfMData.

    Returns:
        (IntrinsicsTransforming node, ExportImages node)
    """
    intrinsics = g.addNewNode("IntrinsicsTransforming", input=inputSfm, type="pinhole")
    export = g.addNewNode("ExportImages", input=intrinsics.input, target=intrinsics.output,
                          outputFileType=outputFileType)
    export.masksFolders.append(segmentation.output)
    return intrinsics, export


def selectViews(g, nodes, expression, transferLandmarks):
    """Views of CameraInit selected on their original path, with the poses and intrinsics of the SfM."""
    views = g.addNewNode("SfMFilter", inputFile=nodes["cameraInit"].output, expression=expression)
    return g.addNewNode("SfMTransfer", input=views.outputSfMData_selected, reference=nodes["sfm"].output,
                        method="from_viewid", transferLandmarks=transferLandmarks)


def build(name, prompt, maskFeatures, turntableTags, albedo=False):
    """MVPS template with LINO-UniPS. albedo: also estimate the albedo maps (LINO-UniPS PBR network), used by
    RNb-NeuS2 and to texture its mesh."""
    g, nodes = buildStructureFromMotion(prompt, maskFeatures, turntableTags)
    _, export = addUndistortedImages(g, nodes["sfm"].output, nodes["segmentation"], "png")

    # Workstation settings (16 GB GPU): normal maps at half resolution from at most 10 lighting images per pose
    # (LINO memory grows with the number of images: 12 images at downscale 2 already peak at ~12 GB), marching cubes at 512.
    # Paper settings (A100): downscale=1, nbImages=-1 (all images), meshResolution=1024.
    # The pose masks (pixels with a normal) drive the RNb-NeuS2 scene normalization: no landmarks needed.
    ps = g.addNewNode("LINOUniPS", inputSfm=export.outputSfMData, downscale=2, nbImages=10, keepLandmarks=False)
    addRNbNeuS2(g, ps, albedo)
    return g


def addRNbNeuS2(g, ps, albedo):
    """RNb-NeuS2 on the normal maps of a universal photometric stereo node; with albedo, the node also estimates the
    albedo maps (normals from its normal network, albedo from its PBR network), RNb-NeuS2 uses them and the mesh is
    textured with them."""
    if not albedo:
        return g.addNewNode("RNbNeuS2", inputNormalSfm=ps.outputSfmDataNormal, inputMaskFolder=ps.outputMaskFolder,
                            scalingMode="silhouettes", meshResolution=512)
    ps.estimateAlbedo.value = True
    rnb = g.addNewNode("RNbNeuS2", inputNormalSfm=ps.outputSfmDataNormal, inputAlbedoSfm=ps.outputSfmDataAlbedo,
                       inputMaskFolder=ps.outputMaskFolder, scalingMode="silhouettes", meshResolution=512)
    addAlbedoTexturing(g, rnb)
    return rnb


# Single-light images of the PS folders: the all-light reference images (biface all_leds-*, calathos LIGHT.NEF,
# gourdan *_all_leds) are not lighting images for a calibrated near-light model
PS_SINGLE_LIGHT = 'contains(path, "/PS/") and match(path, "(?i)(all_leds|ambient)|/LIGHT\\.") == False'


def addProxyMesh(g, nodes):
    """Dense photogrammetry on the MV views only, in the frame of the shared SfM: the geometric proxy of LED-getter.

    Same chain as the photometric stereo branch: only the MV views are undistorted and exported, and DepthMap reads
    these exports. The landmarks of the SfM drive the depth range of DepthMap.
    """
    cameras = selectViews(g, nodes, 'contains(path, "/MV/")', transferLandmarks=True)
    intrinsics, export = addUndistortedImages(g, cameras.output, nodes["segmentation"], "png")
    depthMap = g.addNewNode("DepthMap", input=intrinsics.output, imagesFolder=export.output)
    depthMapFilter = g.addNewNode("DepthMapFilter", input=depthMap.input, depthMapsFolder=depthMap.output)
    meshing = g.addNewNode("Meshing", input=depthMapFilter.input, depthMapsFolder=depthMapFilter.output)
    return g.addNewNode("MeshFiltering", inputMesh=meshing.outputMesh)


# Texturing of the RNb-NeuS2 mesh with the albedo maps: a mesh from outside Meshing and an albedo SfMData without
# landmarks (see the texturing section of the RNb-NeuS2 Meshroom README)
ALBEDO_TEXTURING = dict(
    textureSide=4096,  # Basic unwrap of the RNb mesh: about a quarter of a 4096 atlas
    downscale=1,  # the albedo maps are already at the photometric stereo resolution
    unwrapMethod="Basic",  # RNb meshes have more than 600k faces: LSCM / ABF are not applicable
    visibilityRemappingMethod="MeshItself",  # no landmarks: ray-cast visibility of each vertex
    subdivisionTargetRatio=0.0,  # the subdivision targets the (empty) landmark cloud and makes the binary abort
    workingColorSpace="Linear",  # the albedo is linear: blended in linear space, written as sRGB PNG
    correctEV=False,  # the albedo maps are not exposures
)


def addAlbedoTexturing(g, rnb):
    """Texture the RNb-NeuS2 mesh with the albedo maps harmonized by RNb-NeuS2 (the albedo of each pose is known up
    to a scale per color channel: RNb-NeuS2 brings them to a common scale for its training and outputs them).

    The triangles seen by none of the albedo views (e.g. the back of the calathos plaque, closed by RNb-NeuS2) are
    removed first, with the visibility used by Texturing (MeshItself): the Basic unwrap gives each of them an empty
    chart, packed into empty atlases (calathos: 6 empty atlases, 17 min) and aliceVision_texturing aborts on exit
    with a corrupted heap. They would not be textured anyway.
    """
    seenMesh = g.addNewNode("MeshRemoveUnseenFaces", input=rnb.outputAlbedoSfm, inputMesh=rnb.outputMesh)
    texturing = g.addNewNode("Texturing", input=rnb.outputAlbedoSfm, imagesFolder=rnb.outputAlbedoFolder,
                             inputMesh=seenMesh.outputMesh, **ALBEDO_TEXTURING)
    texturing.colorMapping.colorMappingFileType.value = "png"
    return texturing


def addLedGetterInput(g, psImages, sfm):
    """SfMData of the LED-getter nodes, converted to .sfm JSON (ConvertSfMFormat).

    Workaround: without it, the LED-getter nodes read the .abc/.usda export through the
    AliceVision Python bindings, which fail in the numpy 2 environment of mrLedGetter when the bindings are built
    against numpy 1 (nightly bundle). Kept in the templates until this is fixed.
    """
    convert = g.addNewNode("ConvertSfMFormat", input=psImages.outputSfMData, fileExt="sfm",
                           describerTypes=list(sfm.describerTypes.value))
    return convert.output


def build_ledgetter(name, prompt, maskFeatures, turntableTags, withPhotometricStereo=True):
    """MVPS template with LED-getter (self-calibrated near-light photometric stereo on a photogrammetric proxy).

    The PS single-light images are exported as linear EXR (LED-getter needs linear radiometry), read from the RAW files
    with the poses of the shared SfM. withPhotometricStereo=False stops at the proxy mesh (test of the dense branch).
    """
    g, nodes = buildStructureFromMotion(prompt, maskFeatures, turntableTags)
    proxy = addProxyMesh(g, nodes)
    if not withPhotometricStereo:
        return g

    psCameras = selectViews(g, nodes, PS_SINGLE_LIGHT, transferLandmarks=False)
    _, psImages = addUndistortedImages(g, psCameras.output, nodes["segmentation"], "exr")

    # Workstation settings, as for LINO: lights and normal maps at half resolution. Paper settings: downscale=1.
    ledInput = addLedGetterInput(g, psImages, nodes["sfm"])
    lights = g.addNewNode("LedGetterLights", inputSfm=ledInput, inputMesh=proxy.outputMesh, downscale=2,
                          lightRig=name.split("_ledgetter")[0] in LIGHT_RIG_OBJECTS)
    ps = g.addNewNode("LedGetterPS", inputSfm=ledInput, inputMesh=proxy.outputMesh,
                      inputLights=lights.outputFolder, downscale=2)
    # LED-getter also estimates the albedo: RNb-NeuS2 uses it (two-phase training with albedo scaling)
    rnb = g.addNewNode("RNbNeuS2", inputNormalSfm=ps.outputSfmDataNormal, inputAlbedoSfm=ps.outputSfmDataAlbedo,
                       inputMaskFolder=ps.outputMaskFolder, scalingMode="silhouettes", meshResolution=512)
    addAlbedoTexturing(g, rnb)
    return g


# Reference image of each PS folder of the PS-only objects (filename pattern, see buildPsOnlyFrontEnd)
POSE_REFERENCE_PATTERN = "all_leds"


def buildPsOnlyFrontEnd(prompt, namingMode="keep"):
    """PS-only front end: one multi-lighting folder per pose, calibrated and segmented on one reference image per pose.

    Each PS/PS_xx folder holds the single-light images and one reference image whose filename contains
    POSE_REFERENCE_PATTERN (Gourdan: lit by all the LEDs). CameraInit groups the images of a folder under one poseId
    (the viewId of the middle image of the sequence, without an image named 'ambient'). Only the reference images are
    developed (EXR), segmented (SAM3) and used for the structure from motion; the poses and intrinsics are then
    transferred to all the RAW images of the folder (same poseId), and the photometric stereo uses the single-light
    images only (excludePoseReferenceImage), with the mask of the reference image as pose mask (maskPoseReferenceOnly:
    the alpha of the other images only holds the valid area of the undistortion). The PS nodes find the reference
    image by its filename (poseReferencePattern): the images are exported with their original names (namingMode
    'keep'; 'viewid' for the readers that need <viewId> names, e.g. DepthMap).
    """
    g = Graph("")
    cameraInit = g.addNewNode("CameraInit")

    # Reference images, selected on their original filename (before ImageProcessing renames them <viewId>.exr)
    references = g.addNewNode("SfMFilter", inputFile=cameraInit.output, expression='contains(lower(path), "{}")'.format(POSE_REFERENCE_PATTERN))
    # Only the reference images are developed: SAM3 cannot read NEF files
    referenceImages = g.addNewNode("ImageProcessing", input=references.outputSfMData_selected, extension="exr")

    segmentation = g.addNewNode("ImageSegmentationSam3", input=referenceImages.outSfMData, prompt=prompt,
                                extensionOut="png")
    extraction = g.addNewNode("FeatureExtraction", input=referenceImages.outSfMData, masksFolder=segmentation.output,
                              describerTypes=["dspsift"])
    imageMatching = g.addNewNode("ImageMatching", input=referenceImages.outSfMData)
    imageMatching.featuresFolders.resetToDefaultValue()
    imageMatching.featuresFolders.append(extraction.output)
    featureMatching = g.addNewNode("FeatureMatching", input=imageMatching.input, imagePairsList=imageMatching.output,
                                   featuresFolders=imageMatching.featuresFolders, describerTypes=["dspsift"])
    sfm = g.addNewNode("StructureFromMotion", input=featureMatching.input,
                       featuresFolders=featureMatching.featuresFolders, describerTypes=["dspsift"])
    sfm.matchesFolders.append(featureMatching.output)

    # All the images of a folder share the poseId of its reference image: the transfer gives them pose and intrinsics.
    # ExportImages then reads the RAW files directly, with the same RAW settings as ImageProcessing (identical pixels).
    transfer = g.addNewNode("SfMTransfer", input=cameraInit.output, reference=sfm.output, method="from_viewid",
                            transferLandmarks=False)
    intrinsics = g.addNewNode("IntrinsicsTransforming", input=transfer.output, type="pinhole")
    export = g.addNewNode("ExportImages", input=intrinsics.input, target=intrinsics.output, outputFileType="png",
                          namingMode=namingMode)
    export.masksFolders.append(segmentation.output)  # only the reference images have a mask (alpha channel)
    return g, {"segmentation": segmentation, "sfm": sfm, "intrinsics": intrinsics, "export": export}


def build_ps_only(prompt, method="LINOUniPS", albedo=False):
    """PS-only graph (buildPsOnlyFrontEnd) with a universal photometric stereo node (LINOUniPS, UniMSPS: same
    psCommon inputs) and RNb-NeuS2 (albedo: see addRNbNeuS2, LINOUniPS only)."""
    g, nodes = buildPsOnlyFrontEnd(prompt)
    # Same workstation settings as build()
    ps = g.addNewNode(method, inputSfm=nodes["export"].outputSfMData, downscale=2, nbImages=10, keepLandmarks=False,
                      excludePoseReferenceImage=True, maskPoseReferenceOnly=True,
                      poseReferencePattern=POSE_REFERENCE_PATTERN)
    addRNbNeuS2(g, ps, albedo)
    return g


def build_ps_only_ledgetter(name, prompt):
    """PS-only graph with LED-getter: the photogrammetric proxy comes from the pose reference images.

    Without a separate MV set, the dense photogrammetry runs on the reference images of the structure from motion (one
    all-LED image per pose), read undistorted from the PNG exports. All the PS images are exported as linear EXR,
    reference images included: they hold the pose masks (maskPoseReferenceOnly) but are not lighting images
    (excludePoseReferenceImage).
    """
    g, nodes = buildPsOnlyFrontEnd(prompt, namingMode="viewid")  # DepthMap reads <viewId>.png
    references = g.addNewNode("IntrinsicsTransforming", input=nodes["sfm"].output, type="pinhole")
    depthMap = g.addNewNode("DepthMap", input=references.output, imagesFolder=nodes["export"].output)
    depthMapFilter = g.addNewNode("DepthMapFilter", input=depthMap.input, depthMapsFolder=depthMap.output)
    meshing = g.addNewNode("Meshing", input=depthMapFilter.input, depthMapsFolder=depthMapFilter.output)
    proxy = g.addNewNode("MeshFiltering", inputMesh=meshing.outputMesh)

    intrinsics = nodes["intrinsics"]
    psImages = g.addNewNode("ExportImages", input=intrinsics.input, target=intrinsics.output, outputFileType="exr",
                            namingMode="keep")
    psImages.masksFolders.append(nodes["segmentation"].output)
    # Same workstation settings as build_ledgetter()
    poseReference = {"excludePoseReferenceImage": True, "maskPoseReferenceOnly": True,
                     "poseReferencePattern": POSE_REFERENCE_PATTERN}
    ledInput = addLedGetterInput(g, psImages, nodes["sfm"])
    lights = g.addNewNode("LedGetterLights", inputSfm=ledInput, inputMesh=proxy.outputMesh, downscale=2,
                          lightRig=name in LIGHT_RIG_OBJECTS, **poseReference)
    ps = g.addNewNode("LedGetterPS", inputSfm=ledInput, inputMesh=proxy.outputMesh,
                      inputLights=lights.outputFolder, downscale=2, **poseReference)
    rnb = g.addNewNode("RNbNeuS2", inputNormalSfm=ps.outputSfmDataNormal, inputAlbedoSfm=ps.outputSfmDataAlbedo,
                       inputMaskFolder=ps.outputMaskFolder, scalingMode="silhouettes", meshResolution=512)
    addAlbedoTexturing(g, rnb)
    return g


def main():
    tree = sys.argv[1] == "--tree"
    args = sys.argv[2:] if tree else sys.argv[1:]
    outFolder = args[0]
    names = list(PUBLISHED) if tree else (args[1:] or list(OBJECTS) + list(PS_ONLY_OBJECTS))
    meshroom.core.initPlugins()
    meshroom.core.initNodes()
    os.makedirs(outFolder, exist_ok=True)
    for name in names:
        if name.endswith("_ledgetter_proxy"):  # test of the dense branch only (no LED-getter node needed)
            g = build_ledgetter(name, *OBJECTS[name[:-len("_ledgetter_proxy")]], withPhotometricStereo=False)
        elif name.endswith("_ledgetter") and name[:-len("_ledgetter")] in PS_ONLY_OBJECTS:
            g = build_ps_only_ledgetter(name[:-len("_ledgetter")], PS_ONLY_OBJECTS[name[:-len("_ledgetter")]])
        elif name.endswith("_ledgetter"):
            g = build_ledgetter(name, *OBJECTS[name[:-len("_ledgetter")]])
        elif name.endswith("_lino") and name[:-len("_lino")] in PS_ONLY_OBJECTS:
            g = build_ps_only(PS_ONLY_OBJECTS[name[:-len("_lino")]], albedo=True)
        elif name.endswith("_lino"):
            g = build(name, *OBJECTS[name[:-len("_lino")]], albedo=True)
        elif name.endswith("_unimsps") and name[:-len("_unimsps")] in PS_ONLY_OBJECTS:
            g = build_ps_only(PS_ONLY_OBJECTS[name[:-len("_unimsps")]], method="UniMSPS")
        elif name in PS_ONLY_OBJECTS:
            g = build_ps_only(PS_ONLY_OBJECTS[name])
        else:
            g = build(name, *OBJECTS[name])
        path = os.path.join(outFolder, PUBLISHED[name] if tree else name + ".mgt")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        g.save(path, template=True)
        print("Saved", path, "-", len(g.nodes), "nodes,", len(g.edges), "edges")


if __name__ == "__main__":
    main()
