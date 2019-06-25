import bpy
import os
import subprocess
import tempfile
import shutil

from io_scene_usdz.file_data import *
from io_scene_usdz.scene_data import *

def export_usdz(context, filepath = '', materials = True, keepUSDA = False,
                bakeTextures = False, bakeAO = False, samples = 64,
                scale = 1.0, animated = False, useConverter = False,
                bakeSize = 1024):
    filePath, fileName = os.path.split(filepath)
    fileName, fileType = fileName.split('.')

    usdaFile = filePath+'/'+fileName+'.usda'
    usdcFile = filePath+'/'+fileName+'.usdc'
    usdzFile = filePath+'/'+fileName+'.usdz'

    tempPath = None
    if not keepUSDA:
        tempPath = tempfile.mkdtemp()
        filePath = tempPath
        usdaFile = tempPath+'/'+fileName+'.usda'
        usdcFile = tempPath+'/'+fileName+'.usdc'

    scene = Scene()
    scene.exportMaterials = materials
    scene.exportPath = filePath
    scene.bakeAO = bakeAO
    scene.bakeTextures = bakeTextures
    scene.bakeSamples = samples
    scene.bakeSize = bakeSize
    scene.scale = scale
    scene.animated = animated
    scene.loadContext(context)

    if bakeTextures or bakeAO:
        scene.exportBakedTextures()

    # Export image files
    data = scene.exportFileData()

    if useConverter:
        # Crate text usda file and run the USDZ Converter Tool
        data.writeUsda(usdaFile)
        args = ['xcrun', 'usdz_converter', usdaFile, usdzFile]
        args += ['-v']
        subprocess.run(args)
    else:
        if keepUSDA:
            data.writeUsda(usdaFile)
        # Create Binary and Manually zip to a usdz file
        data.writeUsdc(usdcFile)
        usdz = UsdzFile(usdzFile)
        usdz.addFile(usdcFile)
        for textureFile in scene.textureFilePaths:
            usdz.addFile(textureFile)
        usdz.close()

    scene.cleanup()
    if tempPath != None:
        shutil.rmtree(tempPath)

    return {'FINISHED'}
