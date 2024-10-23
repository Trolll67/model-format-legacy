# Author: Trolll, https://github.com/Trolll67, https://vk.com/trolll67
# Date: 2024-10-23
# Description: Blender 2.49b plugin to import RMB and RAB files
#
# License: GNU General Public License v3.0
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

#!BPY

"""
Name: 'R2 Online Import .rmb/.rab/.txt'
Blender: 249
Group: 'Import'
Tooltip: 'Import .rmb/.rab/.txt files'
"""

import random
import struct
import os
import Blender
import bpy
# from Blender import Scene, Mesh, Window, sys
from Blender.Mathutils import Matrix, Vector, TranslationMatrix, Quaternion


class BinaryReader():
	def __init__(self, file):
		self.inputFile = file
		self.endian = '<'
		self.mode = self.inputFile.mode if hasattr(self.inputFile, 'mode') else None

	def dirname(self):
		return os.path.dirname(self.inputFile.name)

	def tell(self):
		val = self.inputFile.tell()
		return val

	def size(self):
		back = self.inputFile.tell()
		self.inputFile.seek(0, 2)
		tell = self.inputFile.tell()
		self.inputFile.seek(back)
		return tell
			
	def tell(self):
		val = self.inputFile.tell()
		return val

	def read_uint8(self):
		if self.mode != 'rb':
			return None
		
		data = self.inputFile.read(1)
		data = struct.unpack(self.endian+'B', data)[0]
		return data

	def read_uint16(self):
		if self.mode != 'rb':
			return None
		
		data = self.inputFile.read(2)
		data = struct.unpack(self.endian+'H', data)[0]
		return data

	def read_int32(self):
		if self.mode != 'rb':
			return None
		
		data = self.inputFile.read(4)
		data = struct.unpack(self.endian+'i', data)[0]
		return data

	def read_float32(self):
		if self.mode != 'rb':
			return None
		
		data = self.inputFile.read(4)
		data = struct.unpack(self.endian+'f', data)[0]
		return data

	def read_string(self, limit=1000):
		if self.mode != 'rb':
			return None
		
		completed = False
		data = ''
		for i in range(limit):
			char = struct.unpack('c', self.inputFile.read(1))[0]
			if char == b'\x00' or completed == True:
				completed = True
				continue # not break to set cursor to right position

			try:
				data += char.decode('utf-8')
			except UnicodeDecodeError:
				pass

		return data

	def read_matrix4x4(self):
		if self.mode != 'rb':
			return None
		
		data = self.inputFile.read(16*4)
		data = struct.unpack(self.endian+16*'f', data)

		return list(data)

	def read_unknown(self, count):
		if self.mode != 'rb':
			return None
		
		data = self.inputFile.read(count)
		return data

class Utils():
	@staticmethod
	def Matrix4x4(data):
		return Matrix(data[:4], data[4:8], data[8:12], data[12:16])
	
	@staticmethod
	def RoundVector(vec, dec=17):
		fvec=[]
		for v in vec:
			fvec.append(round(v, dec))
		return Vector(fvec)

	@staticmethod
	def RoundMatrix(mat, dec=17):
		fmat = []
		for row in mat:
			fmat.append(Utils.RoundVector(row,dec))
		return Matrix(*fmat)
	
	@staticmethod
	def VectorMatrix(vector):
		return TranslationMatrix(Vector(vector))
	
	@staticmethod
	def QuatMatrix(quat):
		return Quaternion(quat[3], quat[0], quat[1], quat[2]).toMatrix()	


class DDSTexture():
	def __init__(self, diffuse=None, specular=None, normal=None):
		self.diffuse = diffuse
		self.specular = specular
		self.normal = normal

class RMBMesh():
	def __init__(self):
		self.name = None
		self.parent_bone = None
		self.mesh = None
		self.object = None
		self.has_armature = False
		self.texture_index = 0
		self.bone_map_count = 0
		self.vertices_count = 0
		self.indices_count = 0
		self.indice_list = []
		self.vert_pos_list=[]
		self.vert_norm_list=[]
		self.vert_uv_list = []
		self.face_uv_list = []
		self.skin_list = []
		self.skin_weight_list = []
		self.skin_indice_list = []
		self.skin_id_list = []
		self.bone_name_list = []
		self.BINDSKELETON = None
		self.material_list = []
		self.material_id_list = []
		self.face_list = []
		self.matrix = None
		self.triangle_list = []

	def indices_to_triangles(self, indices_list, material_id):
		for m in range(0, len(indices_list), 3):
			self.triangle_list.append(indices_list[m:m+3])
			self.material_id_list.append(material_id)

	def add_faces(self):
		if len(self.material_list) == 0:
			if len(self.face_list) != 0:
				self.triangle_list = self.face_list
			if len(self.indice_list) != 0:
				self.indices_to_triangles(self.indice_list, 0)
		else:
			if len(self.face_list) > 0:
				if len(self.material_id_list) == 0:
					for material_id in range(len(self.material_list)):
						material = self.material_list[material_id] 
						if material.id_start is not None and material.id_count is not None:
							for face_id in range(material.id_count):
								self.triangle_list.append(self.face_list[material.id_start+face_id])
								self.material_id_list.append(material_id)
						else:
							if material.id_start == None:
								material.id_start = 0
							if material.id_count == None:
								material.id_count = len(self.face_list)
							for face_id in range(material.id_count):
								self.triangle_list.append(self.face_list[material.id_start+face_id])
								self.material_id_list.append(material_id)		
				else:			
					self.triangle_list = self.face_list
						
			if len(self.indice_list)>0:
				for material_id in range(len(self.material_list)):
					material = self.material_list[material_id] 
					if material.id_start == None:
						material.id_start = 0
					if material.id_count == None:
						material.id_count = len(self.indice_list)
					indice_list = self.indice_list[material.id_start:material.id_start+material.id_count]
					self.indices_to_triangles(indice_list, material_id)

	def add_skin_id_list(self):
		if len(self.skin_id_list) == 0:
			for skin_id in range(len(self.skin_list)):
				skin = self.skin_list[skin_id]
				if skin.id_start == None:
					skin.id_start = 0
				if skin.id_count == None:
					skin.id_count = len(self.skin_indice_list)
				for vert_id in range(skin.id_count):
					self.skin_id_list.append(skin_id)

	def add_mesh(self):
		self.mesh = bpy.data.meshes.new(self.name)
		self.mesh.verts.extend(self.vert_pos_list)
		if len(self.vert_norm_list) > 0:
			for i,vert in enumerate(self.mesh.verts):
				vert.no = Vector(self.vert_norm_list[i])
			
		self.mesh.faces.extend(self.triangle_list, ignoreDups=True)
		scene = bpy.data.scenes.active
		self.object = scene.objects.new(self.mesh, self.name)

	def add_vertex_uv(self, blenderMesh, mesh):
		blenderMesh.vertexUV = 1
		for m in range(len(blenderMesh.verts)):
			blenderMesh.verts[m].uvco = Vector(mesh.vert_uv_list[m][0], 1-mesh.vert_uv_list[m][1])	
			# blenderMesh.verts[m].uvco = Vector(mesh.vertUVList[m])

	def add_face_uv(self, blenderMesh, mesh):
		if len(blenderMesh.faces) > 0:
			blenderMesh.faceUV = 1
			
			if len(mesh.vert_uv_list) > 0:
				for id in range(len(blenderMesh.faces)):			
					face = blenderMesh.faces[id]
					face.uv = [v.uvco for v in face.verts]
					face.smooth = 1
					if len(mesh.material_id_list) > 0:
						face.mat = mesh.material_id_list[id] 
			
			if len(mesh.material_id_list) > 0:
				for id in range(len(blenderMesh.faces)):	
					face = blenderMesh.faces[id]
					face.smooth = 1 
					face.mat = mesh.material_id_list[id]
			
			if len(mesh.face_uv_list) > 0:
				for id in range(len(blenderMesh.faces)): 
					face = blenderMesh.faces[id]
					if mesh.face_uv_list[id] is not None:
						face.uv = mesh.face_uv_list[id]
			
			if len(self.vert_norm_list) == 0:			
				blenderMesh.calcNormals()	
			
			blenderMesh.update()
		else:
			print('WARNING: No faces to add UV')

	def add_skin(self, blendMesh, mesh):
		for vert_id in range(len(mesh.skin_id_list)):
			indices = mesh.skin_indice_list[vert_id]
			weights = mesh.skin_weight_list[vert_id]
			skin_id = mesh.skin_id_list[vert_id]
			
			for n in range(len(indices)):
				w  = weights[n]
				if type(w) == int:
					w = w / 255.0

				if w != 0:
					gr_id = indices[n]
					if len(self.bone_name_list) == 0:
						if len(self.skin_list[skin_id].bone_map) > 0:
							gr_name = str(self.skin_list[skin_id].bone_map[gr_id])
						else:	
							gr_name = str(gr_id)
					else:	
						if len(self.skin_list[skin_id].bone_map) > 0:
							gr_name_id = self.skin_list[skin_id].bone_map[gr_id]
							gr_name = self.bone_name_list[gr_name_id]
						else:	
							gr_name = self.bone_name_list[gr_id]

					if gr_name not in blendMesh.getVertGroupNames():
						blendMesh.addVertGroup(gr_name)
					blendMesh.assignVertsToGroup(gr_name, [vert_id], w, 1)

		blendMesh.update()

	def add_bind_pose(self, blendMesh, mesh):
		pose_bones = None
		pose_skeleton = None
		bind_bones = None
		bind_skeleton = None

		if self.BINDSKELETON is not None:
			scene = bpy.data.scenes.active
			for object in scene.objects:
				if object.name == self.BINDSKELETON:
					bind_bones = object.getData().bones
					bind_skeleton = object

		if pose_bones is not None and bind_bones is not None:					
			for vert in blendMesh.verts:
				index = vert.index
				skin_list = blendMesh.getVertexInfluences(index)
				vco = vert.co.copy() * self.object.matrixWorld
				vector = Vector()
				
				for skin in skin_list:
					bone = skin[0]							
					weight = skin[1]
					
					matrix_b = bind_bones[bone].matrix['ARMATURESPACE'] * bind_skeleton.matrixWorld
					matrix_a = pose_bones[bone].matrix['ARMATURESPACE'] * pose_skeleton.matrixWorld
					vector += vco * matrix_a.invert() * matrix_b * weight
					
				vert.co = vector
				
			blendMesh.update()
			Blender.Window.RedrawAll()

	def add_material(self, material, mesh, material_id):
		if material.name is None:
			material.name = self.name + '_mat_' + str(material_id)
		
		blend_material = Blender.Material.New(material.name)
		blend_material.diffuseShader = Blender.Material.Shaders.DIFFUSE_ORENNAYAR
		blend_material.specShader = Blender.Material.Shaders.SPEC_WARDISO
		blend_material.setRms(0.04)
		blend_material.shadeMode = Blender.Material.ShadeModes.CUBIC
		blend_material.rgbCol = material.rgba[:3]
		blend_material.alpha = material.rgba[3]

		# if material.ZTRANS == True:
		# 	blend_material.mode |= Blender.Material.Modes.ZTRANSP
		# 	blend_material.mode |= Blender.Material.Modes.TRANSPSHADOW 
		# 	blend_material.alpha = 0.0
		
		# diffuse texture
		if material.diffuse is not None:
			if os.path.exists(material.diffuse) == True:
				# print('Create texture: {0}'.format(material.diffuse))
				img = Blender.Image.Load(material.diffuse)
				img_name = blend_material.name.replace('_mat_', '_diff_')
				img.setName(img_name)
				texname = blend_material.name.replace('_mat_', '_diff_')
				tex = Blender.Texture.New(texname)
				tex.setType('Image')
				tex.image = img 
				blend_material.setTexture(material.DIFFUSESLOT, tex, Blender.Texture.TexCo.UV, Blender.Texture.MapTo.COL|Blender.Texture.MapTo.ALPHA|Blender.Texture.MapTo.CSP)
		
		# normal texture
		if material.normal is not None:
			if os.path.exists(material.normal) == True:
				img = Blender.Image.Load(material.normal)
				img_name = blend_material.name.replace('_mat_','_norm_')
				img.setName(img_name)
				texname = blend_material.name.replace('_mat_','_norm_')
				tex = Blender.Texture.New(texname)
				tex.setType('Image')
				tex.image = img 
				tex.setImageFlags('NormalMap')
				blend_material.setTexture(material.NORMALSLOT, tex, Blender.Texture.TexCo.UV, Blender.Texture.MapTo.NOR)
				blend_material.getTextures()[material.NORMALSLOT].norfac = material.NORMALSTRONG 
				blend_material.getTextures()[material.NORMALSLOT].mtNor = material.NORMALDIRECTION 
				blend_material.getTextures()[material.NORMALSLOT].size = material.NORMALSIZE
		
		# specular texture
		if material.specular is not None:
			if os.path.exists(material.specular) == True:
				img = Blender.Image.Load(material.specular)
				img_name = blend_material.name.replace('_mat_','_spec_')
				img.setName(img_name)
				texname = blend_material.name.replace('_mat_','_spec_')
				tex = Blender.Texture.New(texname)
				tex.setType('Image')
				tex.image = img 
				blend_material.setTexture(material.SPECULARSLOT, tex, Blender.Texture.TexCo.UV, Blender.Texture.MapTo.CSP)	
				mtextures = blend_material.getTextures() 
				mtex = mtextures[material.SPECULARSLOT]
				mtex.neg = True

		# add material to mesh
		mesh.materials += [blend_material]

		uv_layers = mesh.getUVLayerNames()
		# mesh.activeUVLayer = blend_material.name.replace('_mat_', '_diff_')
		# print('UV Layers:', uv_layers)
		mesh.update()

	def draw(self):
		self.add_faces()
		self.add_skin_id_list()

		self.add_mesh()

		if len(self.triangle_list) > 0:	
			if len(self.vert_uv_list) > 0:
				self.add_vertex_uv(self.mesh,self)
		
		self.add_face_uv(self.mesh, self)
		for material_id in range(len(self.material_list)):
			material = self.material_list[material_id]
			self.add_material(material, self.mesh, material_id)
			
		if self.BINDSKELETON is not None:
			scene = bpy.data.scenes.active
			for object in scene.objects:
				if object.name == self.BINDSKELETON:
					skeleton_matrix = self.object.getMatrix() * object.mat
					#self.object.setMatrix(skeletonMatrix)
					object.makeParentDeform([self.object], 1, 0)

		self.add_skin(self.mesh, self)
		
		if self.matrix is not None:
			self.object.setMatrix(self.matrix * self.object.matrixWorld)
			
		self.add_bind_pose(self.mesh, self)
		Blender.Window.RedrawAll()

class RMBSkeleton:
	def __init__(self):
		self.name = 'armature'
		self.arm_name = 'armature'
		self.bone_list = []
		self.armature = None  
		self.object = None
		self.bone_name_list = []
		self.matrix = None

	def check(self):
		scn = Blender.Scene.GetCurrent()
		scene = bpy.data.scenes.active
		
		for object in scene.objects:
			if object.getType() == 'Armature':
				if object.name == self.name:
					scene.objects.unlink(object)

		for object in bpy.data.objects:
			if object.name == self.name:
				self.object = Blender.Object.Get(self.name)
				self.armature = self.object.getData()
				self.armature.makeEditable()
				for bone in self.armature.bones.values():
					del self.armature.bones[bone.name]
				self.armature.update()

		if self.object == None: 
			self.object = Blender.Object.New('Armature', self.name)
		if self.armature == None: 
			self.armature = Blender.Armature.New(self.arm_name)
			self.object.link(self.armature)

		scn.link(self.object)
		self.armature.drawType = Blender.Armature.STICK
		self.object.drawMode = Blender.Object.DrawModes.XRAY
		self.matrix = self.object.mat

	def create_bones(self):
		self.armature.makeEditable()
		bone_list = []
		
		for bone in self.armature.bones.values():
			if bone.name not in bone_list:
				bone_list.append(bone.name)
		
		for bone_id in range(len(self.bone_list)):
			name = self.bone_list[bone_id].name
			if name is None:
				name = str(bone_id)
				self.bone_list[bone_id].name = name

			self.bone_name_list.append(name)
			
			if name not in bone_list:
				eb = Blender.Armature.Editbone() 
				self.armature.bones[name] = eb
		
		self.armature.update()

	def create_bone_connection(self):
		self.armature.makeEditable()

		for bone_id in range(len(self.bone_list)):
			name = self.bone_list[bone_id].name
			if name is None:
				name = str(bone_id)
			
			bone = self.armature.bones[name]
			parent_id = None
			parent_name = None

			if self.bone_list[bone_id].parent_id is not None:
				parent_id = self.bone_list[bone_id].parent_id
				if parent_id != -1:
					parent_name = self.bone_list[parent_id].name
			
			if self.bone_list[bone_id].parent_name is not None:
				parent_name = self.bone_list[bone_id].parent_name

			if parent_name is not None and parent_name in self.armature.bones.keys():
				parent = self.armature.bones[parent_name]
				if parent_id is not None:
					if parent_id != -1:
						bone.parent = parent
				else:
					bone.parent = parent

		self.armature.update()

	def create_bone_position(self):
		self.armature.makeEditable()

		for m in range(len(self.bone_list)):
			name = self.bone_list[m].name
			rot_matrix = self.bone_list[m].rot_matrix
			pos_matrix = self.bone_list[m].pos_matrix
			# scale_matrix = self.bone_list[m].scale_matrix
			matrix = self.bone_list[m].matrix
			bone = self.armature.bones[name]
			
			if matrix is not None:
				bone.matrix = matrix					
				bvec = bone.tail- bone.head
				bvec.normalize()
				bone.tail = bone.head + 0.01 * bvec
			elif rot_matrix is not None and pos_matrix is not None:
				rot_matrix = Utils.RoundMatrix(rot_matrix, 4)
				pos_matrix = Utils.RoundMatrix(pos_matrix, 4)
				bone.matrix = rot_matrix * pos_matrix
				bvec = bone.tail- bone.head
				bvec.normalize()
				bone.tail = bone.head + 0.01 * bvec
			else:
				print('WARNINIG: rotMatrix or posMatrix or matrix is None')
							
		self.armature.update()
		Blender.Window.RedrawAll()

	def draw(self): 
		self.check()

		if len(self.bone_list) > 0:
			self.create_bones()
			self.create_bone_connection()
			self.create_bone_position()	

class RMBBone:
	def __init__(self):
		self.id = None
		self.name = None
		self.parent_id = None
		self.parent_name = None
		self.quat = None
		self.pos = None
		self.matrix = None
		self.pos_matrix = None
		self.rot_matrix = None
		self.scale_matrix = None
		self.children = []
		self.edit = None

class RMBSkin:
	def __init__(self):
		self.bone_map = []
		self.id_start = None
		self.id_count = None
		self.skeleton = None
		self.skeleton_file = None

class RMBMaterial():
	def __init__(self):
		self.name = None
		self.diffuse = None
		self.specular = None
		self.normal = None
		self.id_start = None
		self.id_count = None
		r = random.randint(0, 255)
		g = random.randint(0, 255)
		b = random.randint(0, 255)
		self.rgba = [r / 255.0, g / 255.0, b / 255.0, 1.0]
		self.DIFFUSESLOT = 0
		self.NORMALSLOT = 1
		self.SPECULARSLOT = 2
		self.NORMALSTRONG = 0.5
		self.NORMALDIRECTION = 1
		self.NORMALSIZE = (1,1,1)

class RABAction:
	def __init__(self):
		self.frame_count = None
		self.name = 'action'
		self.skeleton = 'armature'
		self.bone_list = []
		self.ARMATURESPACE = False
		self.BONESPACE = False
		self.FRAMESORT = False
		self.BONESORT = False

	def set_context(self):
		scn = Blender.Scene.GetCurrent()
		context = scn.getRenderingContext()
		if self.frame_count is not None:
			context.eFrame = self.frame_count

	def draw(self):
		scene = bpy.data.scenes.active
		skeleton = None
		if self.skeleton is not None:
			for object in scene.objects:
				if object.getType() == 'Armature':
					if object.name == self.skeleton:				
						skeleton = object
		else:
			print('WARNING: no armature')

		if skeleton is not None:			
			pose = skeleton.getPose()
			action = Blender.Armature.NLA.NewAction(self.name)
			action.setActive(skeleton)
			
			time_list=[]
			
			for m in range(len(self.bone_list)):
				actionbone = self.bone_list[m]
				name = actionbone.name
				pbone = pose.bones[name]
				Blender.Window.RedrawAll()
				
				if pbone is not None:
					pbone.insertKey(skeleton, 0, [Blender.Object.Pose.ROT, Blender.Object.Pose.LOC], True)
					pose.update()
					
					# position keys
					for n in range(len(actionbone.pos_frame_list)):
						frame = actionbone.pos_frame_list[n]
						time_list.append(frame)
						poskey = actionbone.pos_key_list[n]
						bonematrix = poskey
						
						if pbone.parent:		
							pbone.poseMatrix = bonematrix * pbone.parent.poseMatrix
						else:
							pbone.poseMatrix = bonematrix
						
						pbone.insertKey(skeleton, 1+frame, [Blender.Object.Pose.LOC], True)
						pose.update()	
							
					# rotation keys
					for n in range(len(actionbone.rot_frame_list)):
						frame = actionbone.rot_frame_list[n]
						time_list.append(frame)
						rotkey = actionbone.rot_key_list[n]
						bonematrix = rotkey

						if pbone.parent:		
							pbone.poseMatrix = bonematrix * pbone.parent.poseMatrix
						else:
							pbone.poseMatrix = bonematrix

						pbone.insertKey(skeleton, 1+frame, [Blender.Object.Pose.ROT], True)
						pose.update()
						
			if len(time_list) > 0:	
				self.frame_count = max(time_list)

class RABActionBone:
	def	__init__(self):
		self.name = None
		# position keys
		self.pos_frame_count = 0
		self.pos_frames = []
		self.pos_frame_list = []
		self.pos_key_list = []
		# rotation keys
		self.rot_frame_count = 0
		self.rot_frames = []
		self.rot_frame_list = []
		self.rot_key_list = []
		# matrix keys
		self.matrix_frame_list = []
		self.matrix_key_list = []


class ImportRMB():
	def __init__(self, filepath):
		self.filepath = filepath
		self.filename = os.path.basename(filepath)
		self.filename, self.ext = os.path.splitext(self.filename)

	def get_specific_texture(self, base_name, tex_type):
		filename = base_name.split('.')[0]
		ext = base_name.split('.')[-1]
		filename = filename + tex_type + '.' + ext

		if os.path.exists(filename):
			return filename
		else:
			print('\tTexture not found: {0}'.format(filename), 'WARNING')
			return None

	def parse(self, reader):
		# header - 36 bytes
		item_flag = reader.read_int32()         # 4 bytes item flag
		reader.read_unknown(count=16)           # unknown 16 bytes offset             
		texture_count = reader.read_int32()     # texture count
		mesh_count = reader.read_int32()        # mesh count
		bone_count = reader.read_int32()        # bone count
		data_offset = reader.read_int32()       # data offset

		# print("item_flag: ", item_flag)
		# print("texture_count: ", texture_count)
		# print("mesh_count: ", mesh_count)
		# print("bone_count: ", bone_count)

		# texture path
		# prefs = bpy.context.preferences.addons[__package__].preferences
		# texture_path = prefs.tex_filepath
		texture_path = None # "E:\\map_zone\\models\\texture"
	
		if texture_path is not None and os.path.exists(texture_path):
			texDir = texture_path
		else:
			# find texture path in the same directory as the model
			texDir = os.path.join(reader.dirname(), 'texture')
			if os.path.exists(texDir) == False:
				# find texture path in the parent directory
				texDir = reader.dirname().split('model')[0]+'texture'
				if os.path.exists(texDir) == False:
					texDir = reader.dirname()

		textures = []
		# print('Textures: {0}'.format(texture_count))
		for a in range(texture_count):
			texture = DDSTexture() 
			texname = reader.read_string(limit=260)          # 260 bytes texture name

			texpath = os.path.join(texDir, texname)
			texture.diffuse = texpath
			
			# print('\tTexture: {0} {1}'.format(a, texname))
			# print('\t\tDiffuse: {0}'.format(texpath))

			# get specular texture
			specular = self.get_specific_texture(os.path.join(texDir, texname), '_sp')
			if specular is not None:
				texture.specular = specular
				# print('\t\tSpecular: {0}'.format(specular))

			# get normal texture
			normal = self.get_specific_texture(os.path.join(texDir, texname), '_n')
			if normal is not None:
				texture.normal = normal
				# print('\t\tNormal: {0}'.format(normal))

			textures.append(texture)

		meshes = []	
		for a in range(mesh_count):
			mesh = RMBMesh()	
			
			index = reader.read_int32()                     # 4 bytes index
			m_unknown = reader.read_unknown(count=4)        # unknown 4 bytes offset
			
			mesh.name = reader.read_string(limit=64)        # 64 bytes mesh name
			mesh.parent_bone = reader.read_string(limit=64)  # 64 bytes parent bone name

			# print('\tMesh: {0}'.format(index))
			# print('\t\tName: {0}'.format(mesh.name))
			# print('\t\tParent bone: {0}'.format(mesh.parent_bone))

			mesh.has_armature = reader.read_int32() != 0     # rigged 4 bytes
			mesh.texture_index = reader.read_int32()         # texture index 4 bytes
			mesh.bone_map_count = reader.read_int32()         # boneMapCount 4 bytes
			mesh.vertices_count = reader.read_int32()        # vertexCount 4 bytes
			mesh.indices_count = reader.read_int32()         # indicesCount 4 bytes

			# print('\t\tHasArmature: {0}'.format(mesh.has_armature))
			# print('\t\tTextureIndex: {0}'.format(mesh.texture_index))
			# print('\t\tBoneMapCount: {0}'.format(mesh.bone_map_count))
			# print('\t\tVertexCount: {0}'.format(mesh.vertices_count))
			# print('\t\tIndicesCount: {0}'.format(mesh.indices_count))

			# unknown data
			reader.read_unknown(count=2000)                 # unknown 2000 bytes
			meshes.append(mesh)

		# has armature
		skeleton = RMBSkeleton()
		skeleton.name = self.filename

		# 412 bytes for each bone
		# print('\nBones: {0}'.format(bone_count))
		for a in range(bone_count):
			bone = RMBBone()
			bone.id = reader.read_int32()                               # 4 bytes ID
			bone.parent_id = reader.read_int32()                         # 4 bytes parent ID

			# print('\tBone: {0}'.format(a))
			# print('\t\tID: {0}'.format(bone.id))
			# print('\t\tParent ID: {0}'.format(bone.parent_id))

			unk = reader.read_unknown(count=84)

			bone.name = reader.read_string(limit=64)                    # 64 bytes bone name
			# print('\t\tName: {0}'.format(bone.name))
			
			bone.parent_name = reader.read_string(limit=64)              # 64 bytes parent name
			# print('\t\tParent: {0}'.format(bone.parent_name))
			
			m1 = Utils.Matrix4x4(reader.read_matrix4x4())                     # 16*4=64 bytes matrix
			# print(f'    Matrix1: {m1}')
			m2 = Utils.Matrix4x4(reader.read_matrix4x4())                     # 16*4=64 bytes matrix
			# print(f'    Matrix2: {m2}')
			m3 = Utils.Matrix4x4(reader.read_matrix4x4())
			# print(f'    Matrix3: {m3}')
			bone.matrix = m3.invert()                   				# 16*4=64 bytes matrix
			skeleton.bone_list.append(bone)

		skeleton.draw()

		# print('\nMeshes: {0}'.format(mesh_count))
		for mesh in meshes:
			if not isinstance(mesh, RMBMesh):
				continue

			# 1 * boenMapCount - bone mapping
			# print('Mesh: {0}, BoneMapCount: {1}, hasArmature: {2}'.format(mesh.name, mesh.bone_map_count, mesh.has_armature))
			bone_map_list = []
			for b in range(mesh.bone_map_count):
				bone_map_list.append(reader.read_uint8())        # 1 bytes bone map
			bone_map = tuple(bone_map_list)
															
			# vertices
			for b in range(mesh.vertices_count):               # 12 bytes for each vertex position
				x = reader.read_float32()                      # 4 bytes x
				y = reader.read_float32()                      # 4 bytes y
				z = reader.read_float32()                      # 4 bytes z
				mesh.vert_pos_list.append((x, y, z))

			# vertices normals
			for b in range(mesh.vertices_count):                # 12 bytes for each vertex normal
				x = reader.read_float32()                      # 4 bytes x
				y = reader.read_float32()                      # 4 bytes y
				z = reader.read_float32()                      # 4 bytes z
				mesh.vert_norm_list.append((x, y, z))

			# uv coordinates
			for b in range(mesh.vertices_count):                # 8 bytes for each vertex uv
				x = reader.read_float32()                      # 4 bytes x
				y = reader.read_float32()                      # 4 bytes y
				mesh.vert_uv_list.append((x, y))
			
			# unknown data                                     # vertexCount * 12
			reader.read_unknown(count=mesh.vertices_count*12)   # ???
				
			# unknown data                                     # 26476
			reader.read_unknown(count=mesh.vertices_count*12)   # ???


			# skin setup
			if mesh.has_armature:                               
				for b in range(mesh.vertices_count):            # 16 bytes for each vertex skin weight
					x = reader.read_float32()                  # 4 bytes skin weight
					y = reader.read_float32()                  # 4 bytes skin weight
					z = reader.read_float32()                  # 4 bytes skin weight
					w = reader.read_float32()                  # 4 bytes skin weight
					mesh.skin_weight_list.append((x, y, z, w))
					
				for b in range(mesh.vertices_count):            # 4 bytes for each vertex skin indice
					x = reader.read_uint8()                    # 1 byte skin indice
					y = reader.read_uint8()                    # 1 byte skin indice
					z = reader.read_uint8()                    # 1 byte skin indice
					w = reader.read_uint8()                    # 1 byte skin indice
					mesh.skin_indice_list.append((x, y, z, w))

				skin = RMBSkin()
				skin.bone_map = bone_map

				mesh.skin_list.append(skin)
				mesh.bone_name_list = skeleton.bone_name_list
			else:
				for b in range(mesh.vertices_count):
					mesh.skin_weight_list.append([1.0])
					
				for b in range(mesh.vertices_count):
					mesh.skin_indice_list.append([0])
					
				skin = RMBSkin()
				skin.bone_map = [0]

				mesh.skin_list.append(skin)
				mesh.bone_name_list = [mesh.parent_bone]
			

			# indices
			for b in range(mesh.indices_count):
				mesh.indice_list.append(reader.read_uint16())   # 2 bytes indice

			mesh.BINDSKELETON = skeleton.name if skeleton != None else None

			material = RMBMaterial()
			if mesh.texture_index < len(textures):
				material.diffuse = textures[mesh.texture_index].diffuse
				material.specular = textures[mesh.texture_index].specular
				material.normal = textures[mesh.texture_index].normal
			else:
				print('WARNING: Material index out of range: {0}'.format(mesh.texture_index))

			mesh.material_list.append(material)

			# bind mesh matrix to bone matrix
			# print('Mesh parentBone: {0}'.format(mesh.parent_bone))
			if skeleton != None:
				for bone in skeleton.bone_list:
					if bone.name == mesh.parent_bone:
						mesh.matrix = skeleton.object.getMatrix() * bone.matrix

			mesh.draw()

class ImportRAB():
	def __init__(self, filepath):
		self.filepath = filepath
		self.filename = os.path.basename(filepath)
		self.filename, self.ext = os.path.splitext(self.filename)

	def parse(self, reader):
		if '_' not in self.filename:
			print('ERROR: Invalid filename: {0}'.format(self.filename))
			return

		model_name, anim_name = self.filename.split('_')

		action = RABAction()
		action.BONESPACE = True
		action.BONESORT = True
		action.name = 'action_' + anim_name
		action.skeleton = model_name

		X1 = reader.read_int32()           # always 2
		X2 = reader.read_int32()           # always 0
		X3 = reader.read_int32()           # unknown data varies from 0 to ~1920
		X4 = reader.read_int32()           # always 30 except for the only one model (m10053) 6
		X5 = reader.read_int32()           # always 160 except for the only one model (m10053) 800
		X6 = reader.read_int32()           # always 0
		X7 = reader.read_int32()           # always 0
		bones_count = reader.read_int32()  # bones count
		X9 = reader.read_int32()           # ?

		# print('X1: {0}'.format(X1))
		# print('X2: {0}'.format(X2))
		# print('X3: {0}'.format(X3))
		# print('X4: {0}'.format(X4))
		# print('X5: {0}'.format(X5))
		# print('X6: {0}'.format(X6))
		# print('X7: {0}'.format(X7))
		# print('X8 BonesCount: {0}'.format(bones_count))
		# print('X9: {0}'.format(X9))

		bones = []
		for i in range(bones_count):
			bone = RABActionBone()
			bone.name = reader.read_string(64)
			bone.rot_frame_count = reader.read_int32()
			bone.pos_frame_count = reader.read_int32()
			bones.append(bone)

		# 	print('Bone: {0}'.format(bone.name))
		# 	print('\tRotFrameCount: {0}'.format(bone.rot_frame_count))
		# 	print('\tPosFrameCount: {0}'.format(bone.pos_frame_count))

		# print('Position: {0}, Offset: {1}'.format(reader.tell(), X9))
		
		for i in range(bones_count):
			bone = bones[i]
			if not isinstance(bone, RABActionBone):
				print('ERROR: bone is not ActionBone: {0}'.format(bone))
				continue

			bone.pos_frames = []
			for j in range(bone.pos_frame_count):
				bone.pos_frames.append(reader.read_int32())

			bone.rot_frames = []
			for j in range(bone.rot_frame_count):
				bone.rot_frames.append(reader.read_int32())
                
			# position keyframes
			for j in range(bone.pos_frame_count):
				v = bone.pos_frames[j] // 160
				bone.pos_frame_list.append(v)

				x = reader.read_float32()
				y = reader.read_float32()
				z = reader.read_float32()
				matrix = Utils.VectorMatrix((x, y, z))
				bone.pos_key_list.append(matrix)

			# rotation keyframes
			for j in range(bone.rot_frame_count):
				v = bone.rot_frames[j] // 160
				bone.rot_frame_list.append(v)

				x = reader.read_float32()
				y = reader.read_float32()
				z = reader.read_float32()
				w = reader.read_float32()
				matrix = Utils.QuatMatrix((x, y, z, w)).resize4x4().invert()

				if j == 0:
					bone.rot_key_list.append(matrix)
				else:
					matrix = bone.rot_key_list[j-1] * matrix
					bone.rot_key_list.append(matrix)

			action.bone_list.append(bone)

		# print('Position: {0}'.format(reader.tell()))
		# print('Total: {0}'.format(reader.size()))

		action.draw()
		action.set_context()


def save_blend(filepath):
	Blender.Save(filepath)

def parse_txt_file(input_file):
	import xml.etree.ElementTree as ET
	with open(input_file, 'r') as file:
		content = file.read()

		root = ET.fromstring(content)

		mesh_file = root.find('.//Mesh/FileName').text

		rab_files = set()
		for action in root.findall('.//Animation/Action/FileName'):
			rab_files.add(action.text)

		rab_files = sorted(rab_files)

		print("Mesh FileName:", mesh_file)
		print("Unique Action FileName files:", rab_files)

		return mesh_file, rab_files

def txt_import(filepath):
	rmb_file, rab_files = parse_txt_file(filepath)

	filename = os.path.splitext(os.path.basename(filepath))[0]
	dirnamepath = os.path.dirname(filepath)
	outputpath = os.path.join('E:\\map_zone\\output_models', filename)

	if not os.path.exists(outputpath):
		os.makedirs(outputpath)

	# import rmb 
	print("RMB File:", os.path.join(dirnamepath, rmb_file))
	rmb_rab_import(os.path.join(dirnamepath, rmb_file))
	save_blend(os.path.join(outputpath, os.path.splitext(rmb_file)[0] + '.blend'))

	# import rab
	for rab_file in rab_files:
		rmb_rab_import(os.path.join(dirnamepath, rab_file))
		save_blend(os.path.join(outputpath, os.path.splitext(rab_file)[0] + '.blend'))

def rmb_rab_import(filepath):
	filename_with_ext = os.path.basename(filepath)
	filename, ext = os.path.splitext(filename_with_ext)

	# print("filename: ", filename)
	# print("ext: ", ext)

	try:
		file = open(filepath, 'rb')
		reader = BinaryReader(file)
	
		if ext == ".rmb":
			importer = ImportRMB(filepath)
			importer.parse(reader)
		elif ext == ".rab":
			importer = ImportRAB(filepath)
			importer.parse(reader)
		elif ext == ".txt":
			txt_import(filepath)
	except Exception as e:
		print('Error reading file: {0}'.format(e))
	finally:
		file.close()


if __name__ == '__main__':
	Blender.Window.FileSelector(rmb_rab_import,'Import .rmb/.rab/.txt','rmb - skinned mesh, rab - animation') 	