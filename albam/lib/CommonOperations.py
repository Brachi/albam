# -*- coding: utf-8 -*-

import bpy
import bmesh
from mathutils import Matrix


def unselect():
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except:
        pass
    for ob in bpy.context.selected_objects:
        ob.select = False
    bpy.ops.object.select_all(action='DESELECT')
    return


def applyTransform():
    unselect()
    for obj in bpy.context.scene.objects:
        obj.select = obj.type == "MESH"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.select_all(action='DESELECT')


def createRootNub(name):
    o = bpy.data.objects.new(name, None)
    #bpy.context.scene.objects.link(o)
    bpy.context.collection.objects.link(o)
    o.matrix_local = Matrix.Identity(4)
    o.show_wire = True
    #o.show_x_ray = True
    o.show_in_front = True
    return o


def deleteObject(obj):
    objs = bpy.data.objects
    objs.remove(objs[obj.name], do_unlink=True)


def getBlenderObjects(blenderType = None, key = None):
    checks = []
    if blenderType != None:
        checks.append(lambda x: x.type == blenderType)
    if key != None:
        checks.append(lambda x: "Type" in x and key in x["Type"])
    return [obj for obj in bpy.context.scene.objects if all((c(obj) for c in checks))]


def getMeshes(key=None):
    return getBlenderObjects("MESH", key)


def getEmpties(key=None):
    return getBlenderObjects("EMPTY", key)


def cloneMesh(original):
    copy = original.copy()
    # bpy.context.scene.objects.link(copy)
    bpy.context.collection.objects.link(copy)
    # bpy.context.scene.objects.active = copy
    bpy.context.view_layer.objects.active = copy
    # original.select = False
    original.select_set(False)
    # copy.select = True
    copy.select_set(True)
    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
    copy.data.transform(copy.matrix_world)
    # then reset matrix to identity

    copy.matrix_world = Matrix()
    for mod in copy.modifiers:
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except:
            pass
    return copy


def joinMesh(source, target, doUpdate=True, translate=[0.0, 0.0, 0.0], alignTo=None):
    bm = bmesh.new()
    bm.from_mesh(source.data)
    bm.from_mesh(target.data)
    bm.to_mesh(target.data)
    #target.data.update()
    deleteObject(source)
    return target


    result = False
    # Check that the passed objects exist and are mesh objects.
    if target != None \
        and target.type == 'MESH' \
        and source != None \
        and source.type == 'MESH':    
        # Get the source and target mesh data, applying any modifiers to the source.
        ### TODO: Should we get this in some other way?
        scene = bpy.context.scene
        sourceMesh = source.to_mesh( scene, True, 'PREVIEW' )
        targetMesh = target.data    
        ### VERTICES ###    
        numVertices = copyVertices(sourceMesh, targetMesh, translate, alignTo)
        ### MATERIALS ###
        materialsMap = copyMaterials(sourceMesh, targetMesh)
        ### FACES ###    
        copyFaces(sourceMesh, targetMesh, numVertices, materialsMap)
        if doUpdate == True:
            targetMesh.update( calc_edges = True )        
        result = True
        deleteObject(source)
    return result

def copyVertices(sourceMesh, targetMesh, translate, alignTo):
    numVertices = len( targetMesh.vertices )
    numAppendVertices = len( sourceMesh.vertices )
    targetMesh.vertices.add( numAppendVertices )    
    for v in range( numAppendVertices ):      
        # Transform the vertex coordinates into that of the new object.
        newLocation = sourceMesh.vertices[ v ].co        
        # Apply align/translate transformations.
        if alignTo != None:
          quat = alignTo.to_track_quat( '-Y', 'Z' )
          mat = quat.to_matrix().to_4x4()
          mat[3][0:3] = translate
          newLocation = mat * newLocation        
        targetMesh.vertices[ numVertices + v ].co = newLocation
    return numVertices
        
def copyMaterials(sourceMesh, targetMesh):
    # We need maintain a map between our source and target materials as we'll be merging, not
    # simply appending like we do with the vertices and faces.
    materialsMap = {}
    # Link any materials to the target that are linked to the source (without duplicating links).
    # Then, when we bring over the faces we'll also bring over the material assignments.
    for sourceMaterialIndex in range( len( sourceMesh.materials ) ):      
      sourceMaterial = sourceMesh.materials[ sourceMaterialIndex ]
      targetHasMaterial = False      
      for targetMaterialIndex in range( len( targetMesh.materials ) ):        
        targetMaterial = targetMesh.materials[ targetMaterialIndex ]
        if sourceMaterial.name == targetMaterial.name:
          targetHasMaterial = True
          materialsMap[ sourceMaterialIndex ] = targetMaterialIndex
          break
          
      if not targetHasMaterial:
        materialsMap[ sourceMaterialIndex ] = len( targetMesh.materials )
        targetMesh.materials.append( sourceMaterial )
    return materialsMap

def copyFaces(sourceMesh, targetMesh, numVertices, materialsMap):
    numFaces = len( targetMesh.polygons  )
    numAppendFaces = len( sourceMesh.polygons  )
    targetMesh.polygons .add( numAppendFaces )    
    for sourceFaceIndex in range( numAppendFaces ):      
        sourceFace = sourceMesh.polygons [ sourceFaceIndex ]
        targetFace = targetMesh.polygons [ sourceFaceIndex + numFaces ]      
        x_fv = sourceFace.vertices
        o_fv = [ i + numVertices for i in x_fv ]        
        # However, we need to offset the index by the number of faces in the host mesh we are appending to.
        if len( x_fv ) == 4:
            targetFace.vertices_raw = o_fv
        else: 
            targetFace.vertices = o_fv    
        # Copy the face smooth and material assignments (only if there are materials to assign).
        targetFace.use_smooth = sourceFace.use_smooth        
        if( len( materialsMap ) > 0 ):
          targetFace.material_index = materialsMap[ sourceFace.material_index ]   